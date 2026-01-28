"""
GoalManager: Manages hierarchical goal tree and determines priorities.

Goals are organized in a tree where each goal may have:
- Prerequisites (other goals that must be completed first)
- A target milestone (what we're trying to achieve)
- Completion criteria (how we know it's done)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum

from factorio_ai_lab.agents.state_tracker import WorldState


class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class Goal:
    """A single goal in the goal tree."""

    id: str
    name: str
    description: str

    # What this goal requires
    requires: List[str] = field(default_factory=list)  # Goal IDs

    # Completion criteria
    items_required: Dict[str, int] = field(default_factory=dict)  # {item: count}
    entities_required: Dict[str, int] = field(default_factory=dict)  # {entity_type: count}

    # Metadata
    priority: int = 50  # 0-100, higher = more important
    category: str = "general"
    estimated_time: int = 60  # seconds

    # Runtime state
    status: GoalStatus = GoalStatus.PENDING
    attempts: int = 0

    def check_completion(self, state: WorldState) -> bool:
        """Check if this goal is completed based on world state."""
        # Check required items
        for item, count in self.items_required.items():
            if not state.has_item(item, count):
                return False

        # Check required entities
        for entity_type, count in self.entities_required.items():
            entities = state.get_entities_by_type(entity_type)
            if len(entities) < count:
                return False

        return True

    def get_target_item(self) -> Optional[str]:
        """Get the primary item this goal is trying to obtain."""
        if self.items_required:
            # Return the first required item
            return next(iter(self.items_required.keys()))
        return None


# Default goal tree for early game progression
DEFAULT_GOAL_TREE: Dict[str, Dict[str, Any]] = {
    # Raw resources (always available)
    "gather_stone": {
        "name": "Gather Stone",
        "description": "Collect stone for basic crafting",
        "items_required": {"stone": 10},
        "priority": 10,
        "category": "raw",
        "estimated_time": 30,
    },
    "gather_coal": {
        "name": "Gather Coal",
        "description": "Collect coal for fuel",
        "items_required": {"coal": 10},
        "priority": 10,
        "category": "raw",
        "estimated_time": 30,
    },
    "gather_iron_ore": {
        "name": "Gather Iron Ore",
        "description": "Collect iron ore for smelting",
        "items_required": {"iron-ore": 20},
        "priority": 10,
        "category": "raw",
        "estimated_time": 30,
    },
    "gather_copper_ore": {
        "name": "Gather Copper Ore",
        "description": "Collect copper ore for smelting",
        "items_required": {"copper-ore": 10},
        "priority": 10,
        "category": "raw",
        "estimated_time": 30,
    },
    # Basic infrastructure
    "craft_furnace": {
        "name": "Craft Stone Furnace",
        "description": "Build your first furnace for smelting",
        "requires": ["gather_stone"],
        "items_required": {"stone-furnace": 1},
        "priority": 20,
        "category": "crafting",
        "estimated_time": 15,
    },
    "place_furnace": {
        "name": "Place Furnace",
        "description": "Place a furnace in the world",
        "requires": ["craft_furnace"],
        "entities_required": {"furnace": 1},
        "priority": 25,
        "category": "building",
        "estimated_time": 10,
    },
    # Smelting
    "smelt_iron": {
        "name": "Smelt Iron Plates",
        "description": "Produce iron plates from ore",
        "requires": ["place_furnace", "gather_iron_ore", "gather_coal"],
        "items_required": {"iron-plate": 10},
        "priority": 30,
        "category": "smelting",
        "estimated_time": 60,
    },
    "smelt_copper": {
        "name": "Smelt Copper Plates",
        "description": "Produce copper plates from ore",
        "requires": ["place_furnace", "gather_copper_ore", "gather_coal"],
        "items_required": {"copper-plate": 5},
        "priority": 30,
        "category": "smelting",
        "estimated_time": 60,
    },
    # Basic crafting
    "craft_gears": {
        "name": "Craft Iron Gear Wheels",
        "description": "Make gears for machinery",
        "requires": ["smelt_iron"],
        "items_required": {"iron-gear-wheel": 6},
        "priority": 35,
        "category": "crafting",
        "estimated_time": 20,
    },
    # Automation milestone
    "craft_burner_drill": {
        "name": "Craft Burner Mining Drill",
        "description": "Build your first automated miner",
        "requires": ["craft_furnace", "smelt_iron", "craft_gears"],
        "items_required": {"burner-mining-drill": 1},
        "priority": 50,
        "category": "automation",
        "estimated_time": 30,
    },
    "place_burner_drill": {
        "name": "Place Burner Drill on Iron",
        "description": "Set up automated iron mining",
        "requires": ["craft_burner_drill"],
        "entities_required": {"burner-mining-drill": 1},
        "priority": 55,
        "category": "automation",
        "estimated_time": 20,
    },
    # Power
    "craft_boiler": {
        "name": "Craft Boiler",
        "description": "Build a boiler for steam power",
        "requires": ["craft_furnace", "smelt_iron"],
        "items_required": {"boiler": 1},
        "priority": 45,
        "category": "power",
        "estimated_time": 30,
    },
    "craft_steam_engine": {
        "name": "Craft Steam Engine",
        "description": "Build a steam engine for power",
        "requires": ["smelt_iron", "craft_gears"],
        "items_required": {"steam-engine": 1},
        "priority": 45,
        "category": "power",
        "estimated_time": 30,
    },
    "setup_steam_power": {
        "name": "Setup Steam Power",
        "description": "Build and connect steam power",
        "requires": ["craft_boiler", "craft_steam_engine"],
        "entities_required": {"steam-engine": 1, "boiler": 1},
        "priority": 60,
        "category": "power",
        "estimated_time": 120,
    },
    # Science
    "craft_red_science": {
        "name": "Craft Red Science Packs",
        "description": "Produce automation science packs",
        "requires": ["smelt_copper", "craft_gears"],
        "items_required": {"automation-science-pack": 10},
        "priority": 70,
        "category": "science",
        "estimated_time": 60,
    },
}


class GoalManager:
    """
    Manages the goal tree and determines what to do next.

    Usage:
        manager = GoalManager(target="craft_burner_drill")
        current_goal = manager.get_current_goal(state)
        manager.mark_complete("gather_stone")
    """

    def __init__(
        self, target: str = "craft_burner_drill", goal_tree: Optional[Dict[str, Dict]] = None
    ):
        self.target = target
        self.goals: Dict[str, Goal] = {}

        # Load goal tree
        tree = goal_tree or DEFAULT_GOAL_TREE
        self._load_goals(tree)

        # Track completion
        self.completed: Set[str] = set()

    def _load_goals(self, tree: Dict[str, Dict]) -> None:
        """Load goals from tree definition."""
        for goal_id, info in tree.items():
            self.goals[goal_id] = Goal(
                id=goal_id,
                name=info.get("name", goal_id),
                description=info.get("description", ""),
                requires=info.get("requires", []),
                items_required=info.get("items_required", {}),
                entities_required=info.get("entities_required", {}),
                priority=info.get("priority", 50),
                category=info.get("category", "general"),
                estimated_time=info.get("estimated_time", 60),
            )

    def get_current_goal(self, state: WorldState) -> Optional[Goal]:
        """
        Get the highest priority goal that can be worked on.

        Returns the goal that:
        1. Is not yet completed
        2. Has all prerequisites completed
        3. Has the highest priority
        """
        # First update completion status from state
        self._update_completions(state)

        # If target is complete, we're done
        if self.target in self.completed:
            return None

        # Find available goals (prerequisites met, not completed)
        available = []
        for goal_id, goal in self.goals.items():
            if goal_id in self.completed:
                continue

            # Check if all prerequisites are met
            prereqs_met = all(req in self.completed for req in goal.requires)
            if prereqs_met:
                available.append(goal)

        if not available:
            return None

        # Sort by priority (highest first), then by whether it's on the path to target
        target_deps = self._get_all_dependencies(self.target)

        def sort_key(goal: Goal):
            on_path = 1 if goal.id in target_deps else 0
            return (-on_path, -goal.priority)

        available.sort(key=sort_key)
        return available[0]

    def _update_completions(self, state: WorldState) -> None:
        """Update completion status based on current state."""
        for goal_id, goal in self.goals.items():
            if goal_id not in self.completed:
                if goal.check_completion(state):
                    self.completed.add(goal_id)
                    goal.status = GoalStatus.COMPLETED
                    print(f"✅ Goal completed: {goal.name}")

    def _get_all_dependencies(self, goal_id: str) -> Set[str]:
        """Get all goals that are dependencies of the target."""
        deps = set()

        def collect_deps(gid: str):
            if gid in deps:
                return
            deps.add(gid)
            goal = self.goals.get(gid)
            if goal:
                for req in goal.requires:
                    collect_deps(req)

        collect_deps(goal_id)
        return deps

    def mark_complete(self, goal_id: str) -> None:
        """Manually mark a goal as complete."""
        if goal_id in self.goals:
            self.completed.add(goal_id)
            self.goals[goal_id].status = GoalStatus.COMPLETED

    def mark_failed(self, goal_id: str) -> None:
        """Mark a goal as failed."""
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            goal.attempts += 1
            if goal.attempts >= 3:
                goal.status = GoalStatus.FAILED
            else:
                goal.status = GoalStatus.PENDING

    def is_complete(self) -> bool:
        """Check if the target goal is complete."""
        return self.target in self.completed

    def get_progress(self) -> Dict[str, Any]:
        """Get progress summary."""
        target_deps = self._get_all_dependencies(self.target)
        completed_deps = target_deps & self.completed

        return {
            "target": self.target,
            "total_goals": len(target_deps),
            "completed_goals": len(completed_deps),
            "percentage": len(completed_deps) / max(1, len(target_deps)) * 100,
            "remaining": list(target_deps - self.completed),
            "completed": list(completed_deps),
        }

    def get_goal_tree_summary(self) -> str:
        """Get a visual summary of the goal tree."""
        lines = [f"🎯 Target: {self.target}", ""]

        progress = self.get_progress()
        lines.append(
            f"Progress: {progress['completed_goals']}/{progress['total_goals']} ({progress['percentage']:.0f}%)"
        )
        lines.append("")

        # Show goals by category
        by_category: Dict[str, List[Goal]] = {}
        for goal in self.goals.values():
            cat = goal.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(goal)

        for category, goals in by_category.items():
            lines.append(f"📁 {category.upper()}")
            for goal in goals:
                status = "✅" if goal.id in self.completed else "⬜"
                lines.append(f"  {status} {goal.name}")

        return "\n".join(lines)
