"""
TaskPlanner: Decomposes goals into executable action sequences.

Uses recipes.json to understand item dependencies and generates
the minimal sequence of actions needed to achieve a goal.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum

from factorio_ai_lab.agents.state_tracker import WorldState


class ActionType(Enum):
    GATHER = "gather"
    CRAFT = "craft"
    PLACE = "place"
    SMELT = "smelt"
    MOVE = "move"
    INSERT = "insert"
    EXTRACT = "extract"
    WAIT = "wait"


@dataclass
class Action:
    """A single executable action."""

    action_type: ActionType
    target: str  # Item/entity name
    quantity: int = 1
    position: Optional[Tuple[float, float]] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_skill_call(self) -> str:
        """Convert to skill library function call."""
        if self.action_type == ActionType.GATHER:
            return f"gather('{self.target}', {self.quantity})"
        elif self.action_type == ActionType.CRAFT:
            return f"craft('{self.target}', {self.quantity})"
        elif self.action_type == ActionType.PLACE:
            return f"place('{self.target}')"
        elif self.action_type == ActionType.SMELT:
            ore = self.extra.get("ore", "iron-ore")
            return f"smelt('{ore}', '{self.target}', {self.quantity})"
        elif self.action_type == ActionType.WAIT:
            return f"sleep({self.quantity})"
        else:
            return f"# Unknown action: {self.action_type}"

    def __str__(self) -> str:
        return f"{self.action_type.value}({self.target}, qty={self.quantity})"


@dataclass
class Recipe:
    """A crafting/smelting recipe."""

    name: str
    category: str  # "crafting", "smelting", "raw", "chemistry"
    ingredients: List[Tuple[str, int]]  # [(item_name, amount), ...]
    yield_count: int = 1
    crafting_time: float = 0.5

    @property
    def is_raw(self) -> bool:
        return self.category == "raw"

    @property
    def is_smelting(self) -> bool:
        return self.category == "smelting"


class RecipeDatabase:
    """Loads and queries recipe information."""

    def __init__(self, recipes_path: Optional[Path] = None):
        if recipes_path is None:
            recipes_path = (
                Path(__file__).parent.parent.parent.parent / "data" / "knowledge" / "recipes.json"
            )

        self.recipes: Dict[str, Recipe] = {}
        self._load_recipes(recipes_path)

    def _load_recipes(self, path: Path) -> None:
        """Load recipes from JSON file."""
        try:
            with open(path, "r") as f:
                data = json.load(f)

            for name, info in data.get("recipes", {}).items():
                ingredients = [(ing["name"], ing["amount"]) for ing in info.get("ingredients", [])]

                self.recipes[name] = Recipe(
                    name=name,
                    category=info.get("category", "crafting"),
                    ingredients=ingredients,
                    yield_count=info.get("yield", 1),
                    crafting_time=info.get("crafting_time", 0.5),
                )
        except Exception as e:
            print(f"Warning: Could not load recipes: {e}")
            self._load_fallback_recipes()

    def _load_fallback_recipes(self) -> None:
        """Minimal built-in recipes for testing."""
        fallback = {
            "stone": Recipe("stone", "raw", []),
            "coal": Recipe("coal", "raw", []),
            "iron-ore": Recipe("iron-ore", "raw", []),
            "copper-ore": Recipe("copper-ore", "raw", []),
            "wood": Recipe("wood", "raw", []),
            "iron-plate": Recipe("iron-plate", "smelting", [("iron-ore", 1)]),
            "copper-plate": Recipe("copper-plate", "smelting", [("copper-ore", 1)]),
            "stone-furnace": Recipe("stone-furnace", "crafting", [("stone", 5)]),
            "iron-gear-wheel": Recipe("iron-gear-wheel", "crafting", [("iron-plate", 2)]),
            "burner-mining-drill": Recipe(
                "burner-mining-drill",
                "crafting",
                [("stone-furnace", 1), ("iron-plate", 3), ("iron-gear-wheel", 3)],
            ),
        }
        self.recipes = fallback

    def get(self, name: str) -> Optional[Recipe]:
        """Get recipe by name (handles name normalization)."""
        normalized = name.lower().replace("_", "-").replace(" ", "-")
        return self.recipes.get(normalized)

    def get_dependencies(self, name: str, visited: Optional[Set[str]] = None) -> List[str]:
        """Get all dependencies for an item recursively (topological order)."""
        if visited is None:
            visited = set()

        normalized = name.lower().replace("_", "-")

        if normalized in visited:
            return []

        visited.add(normalized)
        recipe = self.get(normalized)

        if not recipe or recipe.is_raw:
            return [normalized]

        deps = []
        for ing_name, _ in recipe.ingredients:
            deps.extend(self.get_dependencies(ing_name, visited))

        deps.append(normalized)
        return deps


class TaskPlanner:
    """
    Plans action sequences to achieve goals.

    Uses recipe database to decompose goals into primitive actions,
    accounting for current inventory and world state.
    """

    def __init__(self, recipes_db: Optional[RecipeDatabase] = None):
        self.recipes = recipes_db or RecipeDatabase()

    def plan_item(self, target_item: str, quantity: int, state: WorldState) -> List[Action]:
        """
        Plan actions to obtain a specific item.

        Args:
            target_item: The item to obtain (e.g., "burner-mining-drill")
            quantity: How many to obtain
            state: Current world state

        Returns:
            List of actions in execution order
        """
        normalized = target_item.lower().replace("_", "-")

        # Calculate what we need considering current inventory
        requirements = self._calculate_requirements(normalized, quantity, state)

        # Convert requirements to actions
        actions = self._requirements_to_actions(requirements, state)

        return actions

    def _calculate_requirements(
        self,
        item: str,
        quantity: int,
        state: WorldState,
        requirements: Optional[Dict[str, int]] = None,
    ) -> Dict[str, int]:
        """
        Recursively calculate all required items.

        Returns dict of {item_name: quantity_needed}
        """
        if requirements is None:
            requirements = {}

        recipe = self.recipes.get(item)

        if not recipe:
            # Unknown item, assume raw resource
            self._add_requirement(requirements, item, quantity, state)
            return requirements

        if recipe.is_raw:
            # Raw resource - just need to gather
            self._add_requirement(requirements, item, quantity, state)
            return requirements

        # Calculate how many crafts we need
        have = state.get_item_count(item)
        need = max(0, quantity - have)

        if need == 0:
            return requirements

        # Account for recipe yield
        crafts_needed = (need + recipe.yield_count - 1) // recipe.yield_count

        # Add this item to requirements (will be crafted)
        self._add_requirement(requirements, item, crafts_needed, state)

        # Recursively calculate ingredient requirements
        for ing_name, ing_amount in recipe.ingredients:
            total_ing_needed = ing_amount * crafts_needed
            self._calculate_requirements(ing_name, total_ing_needed, state, requirements)

        return requirements

    def _add_requirement(
        self, requirements: Dict[str, int], item: str, quantity: int, state: WorldState
    ) -> None:
        """Add an item requirement, accounting for inventory."""
        have = state.get_item_count(item)
        current_req = requirements.get(item, 0)
        total_needed = current_req + quantity

        # Only require what we don't have
        actual_need = max(0, total_needed - have)

        if actual_need > 0:
            requirements[item] = actual_need

    def _requirements_to_actions(
        self, requirements: Dict[str, int], state: WorldState
    ) -> List[Action]:
        """
        Convert requirements dict to ordered action list.

        Respects dependency order (raw → smelted → crafted).
        """
        actions: List[Action] = []

        # Group by category
        raw_items = []
        smelt_items = []
        craft_items = []

        for item, qty in requirements.items():
            recipe = self.recipes.get(item)
            if not recipe or recipe.is_raw:
                raw_items.append((item, qty))
            elif recipe.is_smelting:
                smelt_items.append((item, qty))
            else:
                craft_items.append((item, qty))

        # 1. Gather raw resources
        for item, qty in raw_items:
            actions.append(Action(action_type=ActionType.GATHER, target=item, quantity=qty))

        # 2. Ensure we have a furnace for smelting
        if smelt_items and not state.get_entities_by_type("furnace"):
            # Need to build a furnace first
            if not state.has_item("stone-furnace"):
                # Plan furnace creation
                furnace_actions = self.plan_item("stone-furnace", 1, state)
                actions.extend(furnace_actions)

            # Place the furnace
            actions.append(Action(action_type=ActionType.PLACE, target="stone-furnace"))

        # 3. Smelt items
        for item, qty in smelt_items:
            recipe = self.recipes.get(item)
            if recipe and recipe.ingredients:
                ore = recipe.ingredients[0][0]  # First ingredient is the ore
                actions.append(
                    Action(
                        action_type=ActionType.SMELT, target=item, quantity=qty, extra={"ore": ore}
                    )
                )

        # 4. Craft items (in dependency order)
        # Sort by dependency depth
        craft_items_sorted = self._sort_by_dependencies(craft_items)

        for item, qty in craft_items_sorted:
            actions.append(Action(action_type=ActionType.CRAFT, target=item, quantity=qty))

        return actions

    def _sort_by_dependencies(self, items: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
        """Sort items so dependencies come first."""
        # Get dependency order for all items
        dep_order = []
        for item, _ in items:
            deps = self.recipes.get_dependencies(item)
            for dep in deps:
                if dep not in dep_order:
                    dep_order.append(dep)

        # Sort items by their position in dependency order
        def sort_key(item_tuple):
            item, _ = item_tuple
            try:
                return dep_order.index(item)
            except ValueError:
                return len(dep_order)

        return sorted(items, key=sort_key)

    def generate_code(self, actions: List[Action]) -> str:
        """Generate executable Python code from action list."""
        lines = ["# Auto-generated action plan", "# ===========================", ""]

        for i, action in enumerate(actions, 1):
            lines.append(f"# Step {i}: {action}")
            lines.append(action.to_skill_call())
            lines.append("")

        return "\n".join(lines)

    def plan_and_generate(self, target: str, quantity: int, state: WorldState) -> str:
        """Convenience method: plan and generate code in one step."""
        actions = self.plan_item(target, quantity, state)
        return self.generate_code(actions)
