"""
StateTracker: Maintains structured representation of the Factorio world state.

This module parses FLE outputs and maintains a coherent view of:
- Player inventory
- Placed entities and their status
- Nearby resources
- Production metrics
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class PowerStatus(Enum):
    NONE = "none"
    BURNER = "burner"
    STEAM = "steam"
    SOLAR = "solar"
    NUCLEAR = "nuclear"


@dataclass
class Position:
    x: float
    y: float

    def distance_to(self, other: "Position") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __str__(self) -> str:
        return f"({self.x:.1f}, {self.y:.1f})"


@dataclass
class Entity:
    name: str
    position: Position
    direction: str = "NORTH"
    status: str = "NORMAL"
    inventory: Dict[str, int] = field(default_factory=dict)
    fuel: Dict[str, int] = field(default_factory=dict)

    @property
    def is_working(self) -> bool:
        return self.status.upper() == "WORKING"

    @property
    def is_furnace(self) -> bool:
        return "furnace" in self.name.lower()

    @property
    def is_drill(self) -> bool:
        return "drill" in self.name.lower() or "mining" in self.name.lower()

    @property
    def is_power(self) -> bool:
        return any(x in self.name.lower() for x in ["engine", "boiler", "solar", "accumulator"])


@dataclass
class ResourcePatch:
    resource_type: str
    position: Position
    amount: int = 0


@dataclass
class WorldState:
    """Complete snapshot of the world state."""

    # Core state
    inventory: Dict[str, int] = field(default_factory=dict)
    entities: List[Entity] = field(default_factory=list)
    resources_nearby: Dict[str, Position] = field(default_factory=dict)
    player_position: Position = field(default_factory=lambda: Position(0, 0))
    tick: int = 0

    # Derived metrics (computed)
    power_status: PowerStatus = PowerStatus.NONE
    automation_level: int = 0  # 0-5 scale

    # Tracking
    last_update_tick: int = 0
    errors: List[str] = field(default_factory=list)

    def get_item_count(self, item: str) -> int:
        """Get count of an item in inventory, handling name variations."""
        # Normalize name
        normalized = item.lower().replace("_", "-").replace(" ", "-")

        # Check exact match first
        if normalized in self.inventory:
            return self.inventory[normalized]

        # Check variations
        for key, count in self.inventory.items():
            if normalized in key.lower() or key.lower() in normalized:
                return count

        return 0

    def has_item(self, item: str, count: int = 1) -> bool:
        """Check if we have at least 'count' of an item."""
        return self.get_item_count(item) >= count

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities matching a type."""
        normalized = entity_type.lower().replace("_", "-")
        return [e for e in self.entities if normalized in e.name.lower()]

    def get_nearest_resource(self, resource_type: str) -> Optional[Position]:
        """Get position of nearest resource of given type."""
        normalized = resource_type.lower().replace("_", "-")
        for key, pos in self.resources_nearby.items():
            if normalized in key.lower():
                return pos
        return None

    def count_working_entities(self, entity_type: str) -> int:
        """Count entities of a type that are actively working."""
        entities = self.get_entities_by_type(entity_type)
        return sum(1 for e in entities if e.is_working)


class StateTracker:
    """
    Tracks world state by parsing FLE outputs.

    Usage:
        tracker = StateTracker()
        tracker.update(step_result)
        state = tracker.current
    """

    def __init__(self):
        self.current = WorldState()
        self.history: List[WorldState] = []
        self._max_history = 10

    def update(self, stdout: str, stderr: str = "") -> WorldState:
        """
        Update state from FLE step output.

        Args:
            stdout: Standard output from FLE step
            stderr: Standard error from FLE step

        Returns:
            Updated WorldState
        """
        # Save history
        if len(self.history) >= self._max_history:
            self.history.pop(0)
        self.history.append(self.current)

        # Parse outputs
        if stderr:
            self.current.errors.append(stderr[:200])

        # Try to extract structured data from stdout
        self._parse_inventory(stdout)
        self._parse_entities(stdout)
        self._parse_resources(stdout)
        self._update_derived_metrics()

        self.current.last_update_tick += 1

        return self.current

    def _parse_inventory(self, output: str) -> None:
        """Extract inventory information from output."""
        # Pattern: {'item-name': count, ...}
        inventory_pattern = r"[Ii]nventory\s*[=:]?\s*\{([^}]+)\}"
        match = re.search(inventory_pattern, output)

        if match:
            try:
                # Parse the dict-like string
                content = match.group(1)
                # Match 'item-name': count patterns
                item_pattern = r"['\"]([^'\"]+)['\"]:\s*(\d+)"
                items = re.findall(item_pattern, content)

                for item_name, count in items:
                    self.current.inventory[item_name] = int(count)
            except Exception:
                pass

        # Also try direct inventory prints like "🎒 Inventaire Pierre: 5"
        emoji_pattern = r"(?:Inventaire|inventory)[:\s]+([a-zA-Z-_]+)[:\s]+(\d+)"
        for match in re.finditer(emoji_pattern, output, re.IGNORECASE):
            item_name = match.group(1).lower().replace(" ", "-")
            count = int(match.group(2))
            self.current.inventory[item_name] = count

    def _parse_entities(self, output: str) -> None:
        """Extract entity information from output."""
        # Pattern for entity lists: Entity(name='...', position=Position(x=..., y=...), ...)
        entity_pattern = r"(\w+)\([^)]*name=['\"]([^'\"]+)['\"][^)]*position=Position\(x=([0-9.-]+),?\s*y=([0-9.-]+)\)"

        for match in re.finditer(entity_pattern, output):
            entity_type = match.group(1)
            name = match.group(2)
            x = float(match.group(3))
            y = float(match.group(4))

            # Check if we already have this entity
            existing = None
            for e in self.current.entities:
                if e.name == name and e.position.distance_to(Position(x, y)) < 1.0:
                    existing = e
                    break

            if not existing:
                entity = Entity(name=name, position=Position(x, y))
                self.current.entities.append(entity)

        # Also check for status updates
        status_pattern = r"status=EntityStatus\.(\w+)"
        for match in re.finditer(status_pattern, output):
            status = match.group(1)
            # Update most recent entity if we can't match exactly
            if self.current.entities:
                self.current.entities[-1].status = status

    def _parse_resources(self, output: str) -> None:
        """Extract resource positions from output."""
        # Pattern: "🪨 Pierre trouvée à (x, y)" or "Position(x=..., y=...)"
        resource_patterns = [
            (
                r"(?:pierre|stone)\s+(?:trouvée?|found)\s+(?:à|at)\s*\(?([0-9.-]+)[,\s]+([0-9.-]+)",
                "stone",
            ),
            (
                r"(?:charbon|coal)\s+(?:trouvée?|found)\s+(?:à|at)\s*\(?([0-9.-]+)[,\s]+([0-9.-]+)",
                "coal",
            ),
            (
                r"(?:fer|iron)\s+(?:trouvée?|found)\s+(?:à|at)\s*\(?([0-9.-]+)[,\s]+([0-9.-]+)",
                "iron-ore",
            ),
            (
                r"(?:cuivre|copper)\s+(?:trouvée?|found)\s+(?:à|at)\s*\(?([0-9.-]+)[,\s]+([0-9.-]+)",
                "copper-ore",
            ),
        ]

        for pattern, resource_type in resource_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                x = float(match.group(1))
                y = float(match.group(2))
                self.current.resources_nearby[resource_type] = Position(x, y)

    def _update_derived_metrics(self) -> None:
        """Compute derived metrics from raw state."""
        # Power status
        if any(e.is_power and "steam" in e.name for e in self.current.entities):
            self.current.power_status = PowerStatus.STEAM
        elif any(e.is_power and "solar" in e.name for e in self.current.entities):
            self.current.power_status = PowerStatus.SOLAR
        elif any(e.is_drill and "burner" in e.name and e.is_working for e in self.current.entities):
            self.current.power_status = PowerStatus.BURNER
        else:
            self.current.power_status = PowerStatus.NONE

        # Automation level (0-5)
        level = 0
        if self.current.get_entities_by_type("furnace"):
            level = 1
        if self.current.get_entities_by_type("drill"):
            level = 2
        if self.current.get_entities_by_type("inserter"):
            level = 3
        if self.current.get_entities_by_type("belt"):
            level = 4
        if self.current.get_entities_by_type("assembling-machine"):
            level = 5
        self.current.automation_level = level

    def reset(self) -> None:
        """Reset to initial state."""
        self.current = WorldState()
        self.history = []

    def get_summary(self) -> str:
        """Get a human-readable summary of current state."""
        lines = [
            f"📦 Inventory: {len(self.current.inventory)} item types",
            f"🏗️  Entities: {len(self.current.entities)} placed",
            f"⚡ Power: {self.current.power_status.value}",
            f"🤖 Automation: Level {self.current.automation_level}/5",
        ]

        if self.current.inventory:
            top_items = sorted(self.current.inventory.items(), key=lambda x: -x[1])[:5]
            items_str = ", ".join(f"{k}: {v}" for k, v in top_items)
            lines.append(f"   Top items: {items_str}")

        return "\n".join(lines)
