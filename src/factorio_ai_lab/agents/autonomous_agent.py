"""
AutonomousAgent: Main orchestrator for goal-driven Factorio gameplay.

This agent uses GOAP (Goal-Oriented Action Planning) to autonomously
build a Factorio base from scratch. It combines:
- GoalManager: Determines what to work on
- TaskPlanner: Plans how to achieve goals
- StateTracker: Understands the world state
- SkillLibrary: Executes actions

Usage:
    agent = AutonomousAgent(env, target="craft_burner_drill")
    agent.run(max_steps=100)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Any

from factorio_ai_lab.env_adapter import FleEnv
from factorio_ai_lab.agents.state_tracker import StateTracker
from factorio_ai_lab.agents.task_planner import TaskPlanner, Action, ActionType
from factorio_ai_lab.agents.goal_manager import GoalManager, Goal, GoalStatus


@dataclass
class SkillResult:
    """Result of executing a skill."""

    success: bool
    message: str
    stdout: str = ""
    stderr: str = ""
    entities_created: List[str] = field(default_factory=list)
    items_changed: Dict[str, int] = field(default_factory=dict)


class SkillExecutor:
    """
    Executes skills in the FLE environment.

    Wraps skill calls with the necessary imports and error handling.
    """

    # Skills library code to inject
    SKILLS_PREAMBLE = '''
# import factorio_ai_lab.fle_api # NOT NEEDED - Globals provided by FLE
import time

def _safe_move(pos):
    """Move to position with error handling."""
    try:
        move_to(pos)
        return True
    except Exception as e:
        print(f"Move failed: {e}")
        return False

def _safe_nearest(resource):
    """Find nearest resource with fallback."""
    try:
        pos = nearest(resource)
        if pos:
            return pos
        print(f"No {resource} found nearby")
        return None
    except Exception as e:
        print(f"Search failed: {e}")
        return None

def gather(resource_name, quantity=1):
    """Gather a raw resource."""
    resource_map = {
        'stone': Resource.Stone,
        'coal': Resource.Coal,
        'iron-ore': Resource.IronOre,
        'iron_ore': Resource.IronOre,
        'copper-ore': Resource.CopperOre,
        'copper_ore': Resource.CopperOre,
        'wood': Resource.Wood,
    }
    
    res = resource_map.get(resource_name.lower().replace('-', '_').replace(' ', '_'))
    if not res:
        res = resource_map.get(resource_name.lower().replace('_', '-'))
    if not res:
        print(f"Unknown resource: {resource_name}")
        return False
    
    print(f"🌲 Gathering {quantity} {resource_name}...")
    
    for attempt in range(3):
        pos = _safe_nearest(res)
        if not pos:
            print(f"⚠️ No {resource_name} found, trying to explore...")
            # Spiral exploration
            explore_offsets = [(50, 0), (0, 50), (-50, 0), (0, -50), (50, 50)]
            offset = explore_offsets[attempt % len(explore_offsets)]
            try:
                # Get current pos to add offset? No direct access to player pos in API?
                # Just move to absolute distant points
                target = Position(x=offset[0], y=offset[1])
                print(f"🚶 Exploring to {target}...")
                _safe_move(target)
                continue
            except:
                pass
            return False
        
        _safe_move(pos)
        
        try:
            harvested = harvest_resource(pos, quantity=quantity)
            print(f"✅ Harvested {harvested}")
            if harvested >= quantity:
                return True
            # If partial harvest, loop again
            quantity -= harvested
        except Exception as e:
            print(f"⚠️ Harvest attempt {attempt+1} failed: {e}")
            if "LuaEntity" in str(e):
                print("   Entity invalid, finding new target...")
                time.sleep(1)
                continue
            return False
            
    return False

def craft(item_name, quantity=1):
    """Craft an item."""
    proto_map = {
        'stone-furnace': Prototype.StoneFurnace,
        'stone_furnace': Prototype.StoneFurnace,
        'furnace': Prototype.StoneFurnace,
        'iron-gear-wheel': Prototype.IronGearWheel,
        'iron_gear_wheel': Prototype.IronGearWheel,
        'gear': Prototype.IronGearWheel,
        'gears': Prototype.IronGearWheel,
        'burner-mining-drill': Prototype.BurnerMiningDrill,
        'burner_mining_drill': Prototype.BurnerMiningDrill,
        'drill': Prototype.BurnerMiningDrill,
        'burner-inserter': Prototype.BurnerInserter,
        'transport-belt': Prototype.TransportBelt,
        'belt': Prototype.TransportBelt,
        'wooden-chest': Prototype.WoodenChest,
        'chest': Prototype.WoodenChest,
        'boiler': Prototype.Boiler,
        'steam-engine': Prototype.SteamEngine,
        'pipe': Prototype.Pipe,
        'offshore-pump': Prototype.OffshorePump,
    }
    
    normalized = item_name.lower().replace(' ', '-')
    proto = proto_map.get(normalized) or proto_map.get(normalized.replace('-', '_'))
    
    if not proto:
        print(f"Unknown item: {item_name}")
        return False
    
    print(f"🔨 Crafting {quantity} {item_name}...")
    
    try:
        count = craft_item(proto, quantity=quantity)
        if count > 0:
            print(f"✅ Crafted {count}")
            return True
        else:
            print(f"❌ Craft failed (missing resources?)")
            return False
    except Exception as e:
        print(f"❌ Craft error: {e}")
        return False

def place(item_name, on_resource=None):
    """Place an entity in the world."""
    proto_map = {
        'stone-furnace': Prototype.StoneFurnace,
        'furnace': Prototype.StoneFurnace,
        'burner-mining-drill': Prototype.BurnerMiningDrill,
        'drill': Prototype.BurnerMiningDrill,
        'burner-inserter': Prototype.BurnerInserter,
        'inserter': Prototype.BurnerInserter,
        'wooden-chest': Prototype.WoodenChest,
        'chest': Prototype.WoodenChest,
        'boiler': Prototype.Boiler,
        'steam-engine': Prototype.SteamEngine,
    }
    
    resource_map = {
        'iron': Resource.IronOre,
        'iron-ore': Resource.IronOre,
        'copper': Resource.CopperOre,
        'copper-ore': Resource.CopperOre,
        'coal': Resource.Coal,
        'stone': Resource.Stone,
    }
    
    normalized = item_name.lower().replace(' ', '-')
    proto = proto_map.get(normalized) or proto_map.get(normalized.replace('-', '_'))
    
    if not proto:
        print(f"Unknown entity: {item_name}")
        return None
    
    print(f"🏗️ Placing {item_name}...")
    
    # Determine position
    if on_resource:
        res = resource_map.get(on_resource.lower().replace(' ', '-'))
        if res:
            pos = _safe_nearest(res)
            if pos:
                _safe_move(pos)
                try:
                    entity = place_entity(proto, position=pos, direction=Direction.SOUTH)
                    if entity:
                        print(f"✅ Placed on {on_resource}")
                        return entity
                except Exception as e:
                    print(f"❌ Placement failed: {e}")
    
    # Try simple placement near player
    for offset in [(5, 5), (8, 8), (3, 3), (10, 5), (5, 10)]:
        try:
            pos = Position(x=offset[0], y=offset[1])
            _safe_move(pos)
            entity = place_entity(proto, position=pos, direction=Direction.SOUTH)
            if entity:
                print(f"✅ Placed at {pos}")
                return entity
        except Exception:
            continue
    
    print(f"❌ Could not find valid position for {item_name}")
    return None

def smelt(ore_name, product_name, quantity=1):
    """Smelt resources in a furnace."""
    ore_map = {
        'iron-ore': Prototype.IronOre,
        'iron_ore': Prototype.IronOre,
        'copper-ore': Prototype.CopperOre,
        'copper_ore': Prototype.CopperOre,
    }
    
    product_map = {
        'iron-plate': Prototype.IronPlate,
        'iron_plate': Prototype.IronPlate,
        'copper-plate': Prototype.CopperPlate,
        'copper_plate': Prototype.CopperPlate,
    }
    
    ore = ore_map.get(ore_name.lower().replace(' ', '-'))
    product = product_map.get(product_name.lower().replace(' ', '-'))
    
    if not ore or not product:
        print(f"Unknown ore/product: {ore_name}/{product_name}")
        return False
    
    print(f"🔥 Smelting {quantity} {ore_name} -> {product_name}...")
    
    # Find furnace
    furnaces = [e for e in get_entities() if 'furnace' in e.name.lower()]
    if not furnaces:
        print("No furnace found! Building one...")
        gather('stone', 5)
        craft('furnace')
        furnace = place('furnace')
        if not furnace:
            return False
        furnaces = [furnace]
    
    furnace = furnaces[0]
    _safe_move(furnace.position)
    
    # Add fuel
    inv = inspect_inventory()
    coal_count = inv.get(Prototype.Coal, 0)
    if coal_count < quantity:
        print("Need coal for fuel...")
        gather('coal', quantity)
        _safe_move(furnace.position)
    
    try:
        insert_item(Prototype.Coal, furnace, quantity=max(1, quantity//2))
    except Exception as e:
        print(f"Fuel insert warning: {e}")
    
    # Add ore
    inv = inspect_inventory()
    ore_count = inv.get(ore, 0)
    if ore_count < quantity:
        print(f"Need more {ore_name}...")
        gather(ore_name, quantity)
        _safe_move(furnace.position)
    
    try:
        insert_item(ore, furnace, quantity=quantity)
    except Exception as e:
        print(f"Ore insert error: {e}")
        return False
    
    # Wait for smelting
    print(f"⏳ Waiting for smelting ({quantity * 2}s)...")
    sleep(quantity * 2)
    
    # Extract result
    try:
        extract_item(product, furnace, quantity=quantity)
        print(f"✅ Smelted {quantity} {product_name}")
        return True
    except Exception as e:
        print(f"❌ Extract failed: {e}")
        return False

def check_inventory():
    """Print current inventory."""
    inv = inspect_inventory()
    print(f"📦 Inventory: {dict(inv)}")
    return inv

'''

    def __init__(self, env: FleEnv):
        self.env = env

    def execute(self, action: Action) -> SkillResult:
        """Execute a single action in the environment."""
        code = self.SKILLS_PREAMBLE + "\n\n# Execute action:\n" + action.to_skill_call()

        result = self.env.step(code)

        success = not result.stderr and "Error" not in result.stdout and "❌" not in result.stdout

        return SkillResult(
            success=success,
            message=result.stdout[:200] if result.stdout else "No output",
            stdout=result.stdout,
            stderr=result.stderr,
        )

    def execute_code(self, code: str) -> SkillResult:
        """Execute arbitrary code with skills available."""
        full_code = self.SKILLS_PREAMBLE + "\n\n# Execute:\n" + code

        result = self.env.step(full_code)

        success = not result.stderr and "Error" not in result.stdout and "❌" not in result.stdout

        return SkillResult(
            success=success,
            message=result.stdout[:200] if result.stdout else "No output",
            stdout=result.stdout,
            stderr=result.stderr,
        )


class AutonomousAgent:
    """
    Goal-driven autonomous Factorio agent.

    Uses GOAP to determine goals, plans actions with TaskPlanner,
    and executes them using SkillExecutor.
    """

    def __init__(self, env: FleEnv, target: str = "craft_burner_drill", verbose: bool = True):
        self.env = env
        self.target = target
        self.verbose = verbose

        # Components
        self.goal_manager = GoalManager(target=target)
        self.task_planner = TaskPlanner()
        self.state_tracker = StateTracker()
        self.skill_executor = SkillExecutor(env)

        # Runtime state
        self.step_count = 0
        self.action_count = 0
        self.failures = 0
        self.max_consecutive_failures = 10
        self.consecutive_failures = 0

        # Logging
        self.log: List[Dict[str, Any]] = []

    def run(self, max_steps: int = 100) -> Dict[str, Any]:
        """
        Main agent loop.

        Args:
            max_steps: Maximum number of high-level steps to take

        Returns:
            Summary of the run
        """
        start_time = time.time()

        if self.verbose:
            print("=" * 60)
            print("🤖 AUTONOMOUS AGENT STARTED")
            print(f"🎯 Target: {self.target}")
            print("=" * 60)

        # Initial state check
        self._update_state_from_env()

        while self.step_count < max_steps:
            self.step_count += 1

            # Get current goal
            goal = self.goal_manager.get_current_goal(self.state_tracker.current)

            if goal is None:
                if self.goal_manager.is_complete():
                    if self.verbose:
                        print(f"\n🏆 TARGET COMPLETE: {self.target}")
                    break
                else:
                    if self.verbose:
                        print("\n⚠️ No available goals (stuck?)")
                    break

            if self.verbose:
                print(f"\n{'='*50}")
                print(f"📍 Step {self.step_count}: Working on '{goal.name}'")
                print(f"{'='*50}")

            # Execute the goal
            success = self._execute_goal(goal)

            if success:
                self.consecutive_failures = 0
                if self.verbose:
                    progress = self.goal_manager.get_progress()
                    print(f"📊 Progress: {progress['completed_goals']}/{progress['total_goals']}")
            else:
                self.consecutive_failures += 1
                self.failures += 1
                self.goal_manager.mark_failed(goal.id)

                if self.consecutive_failures >= self.max_consecutive_failures:
                    if self.verbose:
                        print("\n🛑 Too many consecutive failures. Stopping.")
                    break

        # Final summary
        elapsed = time.time() - start_time
        progress = self.goal_manager.get_progress()

        summary = {
            "target": self.target,
            "completed": self.goal_manager.is_complete(),
            "steps": self.step_count,
            "actions": self.action_count,
            "failures": self.failures,
            "elapsed_seconds": elapsed,
            "progress": progress,
        }

        if self.verbose:
            print("\n" + "=" * 60)
            print("📊 RUN SUMMARY")
            print("=" * 60)
            print(f"  Target: {self.target}")
            print(f"  Completed: {'✅ YES' if summary['completed'] else '❌ NO'}")
            print(f"  Steps: {self.step_count}")
            print(f"  Actions: {self.action_count}")
            print(f"  Failures: {self.failures}")
            print(f"  Time: {elapsed:.1f}s")
            print(f"  Progress: {progress['percentage']:.0f}%")
            print("=" * 60)

        return summary

    def _execute_goal(self, goal: Goal) -> bool:
        """Execute all actions needed to complete a goal."""
        goal.status = GoalStatus.IN_PROGRESS

        # Get the target item for this goal
        target_item = goal.get_target_item()

        if not target_item:
            # No item target - might be placement goal
            if goal.entities_required:
                entity_type = next(iter(goal.entities_required.keys()))
                return self._execute_placement(entity_type)
            return True

        # Check if we already have what we need
        if self.state_tracker.current.has_item(
            target_item, goal.items_required.get(target_item, 1)
        ):
            if self.verbose:
                print(f"  Already have {target_item} ✅")
            return True

        # Plan actions
        quantity = goal.items_required.get(target_item, 1)
        actions = self.task_planner.plan_item(target_item, quantity, self.state_tracker.current)

        if self.verbose:
            print(f"  Plan: {len(actions)} actions")
            for i, action in enumerate(actions[:5], 1):
                print(f"    {i}. {action}")
            if len(actions) > 5:
                print(f"    ... and {len(actions) - 5} more")

        # Execute actions
        for action in actions:
            self.action_count += 1

            if self.verbose:
                print(f"  ▶ Executing: {action}")

            result = self.skill_executor.execute(action)
            self._update_state_from_env()

            if not result.success:
                if self.verbose:
                    print(f"    ❌ Failed: {result.message}")
                    if result.stderr:
                        print(f"    Error: {result.stderr[:100]}")
                return False
            else:
                if self.verbose:
                    print(f"    ✅ {result.message[:60]}")

            # Check if goal is now complete
            if goal.check_completion(self.state_tracker.current):
                return True

        # Verify completion
        return goal.check_completion(self.state_tracker.current)

    def _execute_placement(self, entity_type: str) -> bool:
        """Execute a placement action."""
        if self.verbose:
            print(f"  Placing {entity_type}...")

        # Check if we have the item
        if not self.state_tracker.current.has_item(entity_type):
            # Need to craft it first
            result = self.skill_executor.execute(
                Action(action_type=ActionType.CRAFT, target=entity_type, quantity=1)
            )
            self._update_state_from_env()

            if not result.success:
                return False

        # Place it
        result = self.skill_executor.execute(
            Action(action_type=ActionType.PLACE, target=entity_type)
        )
        self._update_state_from_env()

        return result.success

    def _update_state_from_env(self) -> None:
        """Update state tracker from environment."""
        # Execute a state check
        result = self.skill_executor.execute_code("check_inventory()\nprint(get_entities())")
        self.state_tracker.update(result.stdout, result.stderr)


def run_autonomous_agent(
    env: FleEnv, target: str = "craft_burner_drill", max_steps: int = 100, verbose: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to run the autonomous agent.

    Args:
        env: FLE environment instance
        target: Goal ID to achieve (see GoalManager for options)
        max_steps: Maximum number of high-level steps
        verbose: Print progress

    Returns:
        Run summary dict
    """
    agent = AutonomousAgent(env, target=target, verbose=verbose)
    return agent.run(max_steps=max_steps)
