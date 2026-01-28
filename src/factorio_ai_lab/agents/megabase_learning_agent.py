"""
Megabase Self-Learning Agent
Combines knowledge base with curriculum learning for megabase construction
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union, cast
from dotenv import load_dotenv

from factorio_ai_lab.env_adapter import FleEnv, StepResult


load_dotenv()

# ============================================================================
# LLM BACKEND: Local MLX (fast) or OpenAI API (fallback)
# ============================================================================

USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "true").lower() == "true"
LOCAL_MODEL_PATH = Path(__file__).parent.parent.parent.parent / "models" / "qwen-1.5b-4bit"

# Initialize local model if available
_local_model = None
_local_tokenizer = None

if USE_LOCAL_MODEL and LOCAL_MODEL_PATH.exists():
    try:
        from mlx_lm import load, generate

        print(f"🚀 Loading local model from {LOCAL_MODEL_PATH}...")
        _local_model, _local_tokenizer = load(str(LOCAL_MODEL_PATH))
        print("✅ Local Qwen2.5-1.5B model loaded! (5x faster inference)")
    except Exception as e:
        print(f"⚠️ Failed to load local model: {e}")
        print("   Falling back to OpenAI API...")
        USE_LOCAL_MODEL = False
else:
    if USE_LOCAL_MODEL:
        print(f"⚠️ Local model not found at {LOCAL_MODEL_PATH}")
        print("   Falling back to OpenAI API...")
    USE_LOCAL_MODEL = False

# OpenAI fallback
if not USE_LOCAL_MODEL:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    client = None  # type: ignore


# Token limits for Qwen2.5-1.5B (32K context, but we keep buffer for output)
MAX_CONTEXT_TOKENS = 28000  # Leave ~4K for output
CHARS_PER_TOKEN_ESTIMATE = 3.5  # Conservative estimate for code/text mix


def estimate_tokens(text_or_chars: str | int) -> int:
    """Rough token estimation (3.5 chars per token for mixed content)."""
    char_count = text_or_chars if isinstance(text_or_chars, int) else len(text_or_chars)
    return int(char_count / CHARS_PER_TOKEN_ESTIMATE)


def _filter_repeated_lines(code: str, max_repeats: int = 2) -> str:
    """Filter out degenerate repeated lines from LLM output.

    Detects when the same line (or very similar lines) appear more than max_repeats times
    consecutively, which indicates the model is stuck in a loop.
    """
    lines = code.split("\n")
    filtered = []
    repeat_count = 0
    last_line = None

    for line in lines:
        # Normalize for comparison (strip whitespace, ignore comments)
        normalized = line.strip()
        if normalized.startswith("#"):
            normalized = normalized[:50]  # Only compare first part of comments

        if normalized == last_line and normalized:
            repeat_count += 1
            if repeat_count >= max_repeats:
                continue  # Skip this repeated line
        else:
            repeat_count = 0
            last_line = normalized

        filtered.append(line)

    result = "\n".join(filtered)

    # If we filtered a lot, warn
    if len(filtered) < len(lines) * 0.7:
        print(f"⚠️ REPETITION FILTER: Removed {len(lines) - len(filtered)} repeated lines")

    return result


def smart_truncate(text: str, max_chars: int, label: str = "") -> str:
    """Truncate text intelligently, keeping start and end."""
    if len(text) <= max_chars:
        return text

    # Keep 70% from start, 30% from end (context usually more important at start)
    start_chars = int(max_chars * 0.7)
    end_chars = int(max_chars * 0.3)

    truncated = (
        text[:start_chars]
        + f"\n\n[...{label} TRUNCATED ({len(text) - max_chars} chars removed)...]\n\n"
        + text[-end_chars:]
    )
    print(f"⚠️ {label} truncated: {len(text)} -> {len(truncated)} chars")
    return truncated


def generate_completion(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    """Generate completion using local model or OpenAI API with smart token management."""

    # Estimate total tokens
    total_chars = len(system_prompt) + len(user_message)
    estimated_tokens = estimate_tokens(total_chars)
    max_input_chars = int(MAX_CONTEXT_TOKENS * CHARS_PER_TOKEN_ESTIMATE)

    # Truncate if needed
    if total_chars > max_input_chars:
        print(f"⚠️ Input too long ({estimated_tokens} est. tokens). Truncating...")

        # Allocate: 60% system, 40% user (system has stable instructions)
        max_system = int(max_input_chars * 0.6)
        max_user = int(max_input_chars * 0.4)

        system_prompt = smart_truncate(system_prompt, max_system, "SYSTEM")
        user_message = smart_truncate(user_message, max_user, "USER")

    if USE_LOCAL_MODEL and _local_model is not None:
        # Import MLX sampling utilities
        from mlx_lm.sample_utils import make_sampler, make_repetition_penalty

        # Format for Qwen chat template
        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n"

        # Create sampler with low temperature for deterministic code generation
        sampler = make_sampler(temp=0.3, top_p=0.9)

        # Create repetition penalty processor
        repetition_processor = make_repetition_penalty(1.15, context_size=256)

        response = generate(
            _local_model,
            _local_tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            sampler=sampler,
            logits_processors=[repetition_processor],
            verbose=False,
        )

        # Post-process: detect and fix degenerate repetition
        response = _filter_repeated_lines(response)
        return response
    else:
        # OpenAI API fallback
        response = client.chat.completions.create(  # type: ignore
            model="gpt-4o-mini",  # Fixed: was gpt-5-mini which doesn't exist
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_completion_tokens=max_tokens,
            temperature=0.3,  # Lower temperature for code generation
        )
        return response.choices[0].message.content or ""


# Determine project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Load megabase prompt
prompt_path = Path(__file__).parent.parent / "prompts" / "megabase_agent.md"
with open(prompt_path, "r") as f:
    megabase_prompt = f.read()

# ============================================================================
# ENHANCED KNOWLEDGE BASE with Curriculum
# ============================================================================


class MegabaseKnowledgeBase:
    """Knowledge base with curriculum phases"""

    PHASES = {
        1: {
            "name": "Early Game",
            "goal": "Mining → Smelting → Green Circuits",
            "metrics": ["PS", "milestones"],
        },
        2: {
            "name": "Mid Game",
            "goal": "Oil → Plastics → Red Circuits",
            "metrics": ["PS", "milestones_weighted"],
        },
        3: {
            "name": "Late Game",
            "goal": "Roboports + Rails + Modules",
            "metrics": ["SPM_estimate", "entity_efficiency"],
        },
        4: {"name": "Modular Bases", "goal": "Stampable blocks", "metrics": ["MegabaseScore"]},
        5: {
            "name": "UPS Optimization",
            "goal": "Refactor + reduce entities",
            "metrics": ["UPS", "inserter_activity"],
        },
    }

    def __init__(self, kb_file: Optional[Union[str, Path]] = None) -> None:
        if kb_file is None:
            kb_dir = PROJECT_ROOT / "data" / "knowledge"
            kb_dir.mkdir(parents=True, exist_ok=True)
            self.kb_file = kb_dir / "megabase_knowledge.json"
        else:
            self.kb_file = Path(kb_file)
        self.knowledge = self.load()

    def load(self) -> Dict[str, Any]:
        if self.kb_file.exists():
            with open(self.kb_file) as f:
                data = json.load(f)
                return cast(Dict[str, Any], data)
        return {
            "current_phase": 1,
            "building_blocks": {},  # Organized by phase
            "successful_patterns": [],
            "failed_attempts": [],
            "phase_milestones": {},  # Track progress per phase
            "stats": {
                "total_experiments": 0,
                "successful": 0,
                "failed": 0,
                "current_ps": 0,
                "max_ps": 0,
                "tutorial_progress": 0,
            },
        }

    def save(self) -> None:
        with open(self.kb_file, "w") as f:
            json.dump(self.knowledge, f, indent=2)

    def get_current_phase(self) -> Dict[str, Any]:
        return self.PHASES[self.knowledge["current_phase"]]

    def advance_phase(self) -> None:
        """Move to next phase when milestones are met"""
        current = self.knowledge["current_phase"]
        if current < 5:
            self.knowledge["current_phase"] += 1
            print(
                f"🎓 ADVANCING TO PHASE {self.knowledge['current_phase']}: {self.PHASES[self.knowledge['current_phase']]['name']}"
            )
            self.save()

    def add_pattern(
        self,
        pattern_type: str,
        code: str,
        phase: int,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add pattern organized by curriculum phase"""
        phase_key = f"phase_{phase}"
        if phase_key not in self.knowledge["building_blocks"]:
            self.knowledge["building_blocks"][phase_key] = []

        block = {
            "type": pattern_type,
            "code": code,
            "phase": phase,
            "metrics": metrics or {},
            "created_at": datetime.now().isoformat(),
            "times_used": 0,
            "success_rate": 1.0,
        }

        self.knowledge["building_blocks"][phase_key].append(block)
        self.save()
        return block

    def get_patterns_for_phase(self, phase: int) -> List[Dict[str, Any]]:
        """Get all validated patterns for a phase"""
        phase_key = f"phase_{phase}"
        return cast(List[Dict[str, Any]], self.knowledge["building_blocks"].get(phase_key, []))

    def record_experiment(
        self,
        pattern: str,
        success: bool,
        phase: int,
        metrics: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        experiment = {
            "pattern": pattern,
            "success": success,
            "phase": phase,
            "metrics": metrics or {},
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }

        if success:
            self.knowledge["successful_patterns"].append(experiment)
            self.knowledge["stats"]["successful"] += 1

            # Update PS tracking
            if metrics and "ps" in metrics:
                self.knowledge["stats"]["current_ps"] = metrics["ps"]
                if metrics["ps"] > self.knowledge["stats"]["max_ps"]:
                    self.knowledge["stats"]["max_ps"] = metrics["ps"]
        else:
            self.knowledge["failed_attempts"].append(experiment)
            self.knowledge["stats"]["failed"] += 1

        self.knowledge["stats"]["total_experiments"] += 1
        self.save()

    def get_next_tutorial_step(self) -> Optional[Dict[str, Any]]:
        """Get the next uncompleted tutorial step"""
        curriculum = self.knowledge.get("building_blocks", {}).get("minibase_curriculum", [])
        if not curriculum:
            return None

        progress = self.knowledge.get("stats", {}).get("tutorial_progress", 0)

        # Determine current step based on order
        for step in curriculum:
            if step["order"] == progress + 1:
                return step
        return None

    def mark_tutorial_step_complete(self) -> None:
        """Advance tutorial progress"""
        self.knowledge["stats"]["tutorial_progress"] = (
            self.knowledge["stats"].get("tutorial_progress", 0) + 1
        )
        self.save()


# ============================================================================
# MEGABASE AGENT
# ============================================================================


class MegabaseAgent:
    """Curriculum-based megabase agent with knowledge persistence"""

    def __init__(self, env: FleEnv, kb: MegabaseKnowledgeBase) -> None:
        self.env = env
        self.kb = kb
        self.memory: List[Dict[str, Any]] = []
        self.current_goal: Optional[str] = None

    def get_system_prompt(self) -> str:
        """Generate context-aware system prompt with curriculum"""
        phase = self.kb.get_current_phase()

        # Get minibase curriculum (priority) or phase_1_bootstrap
        minibase_patterns = self.kb.knowledge["building_blocks"].get("minibase_curriculum", [])
        bootstrap_patterns = self.kb.knowledge["building_blocks"].get("phase_1_bootstrap", [])
        guide_patterns = minibase_patterns if minibase_patterns else bootstrap_patterns

        # Sort by order if available
        guide_patterns = sorted(guide_patterns, key=lambda x: x.get("order", 999))

        # Get the goal if set
        goal = self.kb.knowledge.get("goal", "Build an automated mini-base!")

        # Get learned patterns
        learned_patterns = self.kb.get_patterns_for_phase(self.kb.knowledge["current_phase"])

        # Find next steps to do
        learned_types = {p.get("type") for p in learned_patterns}
        next_steps = [p for p in guide_patterns if p["type"] not in learned_types][:5]

        # Build the guide context
        if next_steps:
            guide_context = "\n".join(
                [
                    f"📋 **ÉTAPE {p.get('order', '?')}**: {p['type']}\n   {p.get('description', '')}\n   ```python\n{p['code'][:300]}...\n   ```"
                    for p in next_steps[:2]
                ]
            )
        else:
            guide_context = "✅ Toutes les étapes du guide sont complétées! Optimise la base."

        # Show what was already learned
        learned_context = (
            "\n".join([f"✅ {p['type']}" for p in learned_patterns[:8]])
            if learned_patterns
            else "Commence par l'étape 1!"
        )

        # Load strategic knowledge
        strategy_tips = self._load_strategy_tips()

        return f"""{megabase_prompt}

{goal}

## CURRENT STATUS

🎯 **Current Phase: {self.kb.knowledge["current_phase"]} - {phase["name"]}**

📊 **Progress**:
- Total Experiments: {self.kb.knowledge["stats"]["total_experiments"]}
- Success Rate: {self.kb.knowledge["stats"]["successful"] / max(1, self.kb.knowledge["stats"]["total_experiments"]) * 100:.1f}%
- Guide Progress: {len(learned_types)}/{len(guide_patterns)} étapes

{strategy_tips}

## 📚 PROCHAINES ÉTAPES DU GUIDE:

{guide_context}

## ✅ DÉJÀ FAIT:
{learned_context}

## INSTRUCTIONS

**SUIS LE GUIDE ÉTAPE PAR ÉTAPE!**
1. Exécute le code de l'étape actuelle
2. Si erreur, corrige et réessaie
3. Une fois réussi, passe à l'étape suivante
4. N'oublie pas move_to() avant de placer des entités!

Generate ONLY Python code. One action at a time.
"""

    def think(self, observation: StepResult) -> str:
        """Execute curriculum step directly or diagnose errors.

        For small LLMs, we FORCE curriculum compliance by:
        1. Executing the curriculum step code directly (no LLM generation)
        2. Only using LLM to diagnose errors when a step fails
        3. Tracking consecutive failures to avoid infinite loops
        """
        tutorial_step = self.kb.get_next_tutorial_step()

        # Check if last step had an error that needs diagnosis
        last_had_error = self.memory and not self.memory[-1].get("success", True)
        consecutive_failures = self._count_consecutive_failures()

        if tutorial_step:
            step_name = tutorial_step["type"]
            step_code = tutorial_step["code"]
            step_desc = tutorial_step.get("description", step_name)

            # If we had an error on this step, use LLM to diagnose and fix
            if last_had_error and consecutive_failures < 3:
                # Extract error from last observation
                last_error = observation.stderr or observation.stdout or "Unknown error"

                # Use LLM ONLY for error diagnosis
                diagnosis_code = self._diagnose_error(
                    step_name=step_name,
                    step_code=step_code,
                    error=last_error,
                    observation=observation,
                )
                return diagnosis_code

            elif consecutive_failures >= 3:
                # Too many failures, skip to next step
                self.kb.mark_tutorial_step_complete()  # Skip to next
                # Get next step if available
                next_step = self.kb.get_next_tutorial_step()
                if next_step:
                    return next_step["code"]
                else:
                    return "print('All curriculum steps attempted')"

            else:
                # Normal case: execute curriculum code directly
                return step_code

        else:
            # All curriculum steps completed - now let LLM be creative
            return self._generate_free_exploration(observation)

    def _count_consecutive_failures(self) -> int:
        """Count how many times the current step has failed consecutively."""
        count = 0
        for mem in reversed(self.memory):
            if not mem.get("success", True):
                count += 1
            else:
                break
        return count

    def _diagnose_error(
        self, step_name: str, step_code: str, error: str, observation: StepResult
    ) -> str:
        """Use LLM to diagnose an error and generate a fix."""

        # Structured diagnosis prompt for small models
        diagnosis_prompt = f"""<error_diagnosis>
<step_that_failed>
{step_name}
</step_that_failed>

<error_message>
{error[:1000]}
</error_message>

<original_code>
{step_code[:500]}
</original_code>

<task>
Fix the error by writing Python code that:
1. First checks what resources/items are available
2. Gathers any missing prerequisites
3. Then attempts the original step goal

Write ONLY the corrected Python code, nothing else.
</task>
</error_diagnosis>"""

        code = generate_completion(
            system_prompt=self._get_minimal_system_prompt(),
            user_message=diagnosis_prompt,
            max_tokens=800,
        )

        # Extract code block if present
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()

        return code

    def _get_minimal_system_prompt(self) -> str:
        """A minimal prompt for error diagnosis - keeps token count low."""
        return """You are a Factorio automation assistant. You fix Python code errors.

Available functions:
- nearest(Resource.X) → Position
- move_to(position) → None
- harvest_resource(position, quantity=N) → int
- craft_item(Prototype.X, quantity=N) → int
- place_entity(Prototype.X, position=Position(x,y)) → Entity
- insert_item(Prototype.X, entity, quantity=N) → None
- inspect_inventory() → Dict
- get_entities() → List

Types: Prototype.Stone, Prototype.StoneFurnace, Prototype.Coal, Prototype.IronOre, Prototype.IronPlate, Prototype.WoodChest
Resources: Resource.Stone, Resource.Coal, Resource.IronOre, Resource.CopperOre, Resource.Wood

ALWAYS check inventory with inspect_inventory() before crafting.
ALWAYS move_to() before placing entities.
Write ONLY valid Python code."""

    def _load_recipes(self, target_item: str = None) -> str:
        """Load recipes from JSON and filter for specific target dependencies recursively."""
        try:
            import json

            # Use the FULL exhaustive database now
            recipe_path = os.path.join(PROJECT_ROOT, "data", "knowledge", "full_recipes.json")
            with open(recipe_path, "r") as f:
                data = json.load(f)

            recipes_db = data.get("recipes", {})

            # If no target, load a default set of basics
            if not target_item:
                target_item = "burner-mining-drill"

            # Recursive dependency walker
            relevant_recipes = set()

            def add_dependencies(item_name):
                # Normalize name (handle basic variations if needed)
                item_name = item_name.lower().replace("_", "-")
                if item_name in recipes_db:
                    relevant_recipes.add(item_name)
                    for ing in recipes_db[item_name].get("ingredients", []):
                        add_dependencies(ing["name"])

            add_dependencies(target_item)
            # Always add basic raw resources just in case
            for raw in ["wood", "stone", "iron-ore", "copper-ore", "coal"]:
                relevant_recipes.add(raw)

            recipes_str = f"# 📖 RECIPE BOOK (FILTERED for {target_item}):\n# | Item | Ingredients | Category |\n# |---|---|---|\n"
            for name in sorted(relevant_recipes):
                if name in recipes_db:
                    details = recipes_db[name]
                    ing_str = ", ".join(
                        [
                            f"{ing['amount']}x {ing['name']}"
                            for ing in details.get("ingredients", [])
                        ]
                    )
                    if not ing_str:
                        ing_str = "(Raw Resource)"
                    recipes_str += f"# | {name} | {ing_str} | {details.get('category')} |\n"

            return recipes_str
        except Exception as e:
            print(f"Error loading recipes: {e}")
            return "# Error loading recipes.json"

    def _load_strategy_tips(self) -> str:
        """Load strategic tips from JSON for context-aware decision making."""
        try:
            tips_path = os.path.join(PROJECT_ROOT, "data", "knowledge", "strategy_tips.json")
            with open(tips_path, "r") as f:
                tips = json.load(f)

            # Extract key sections for the prompt
            sections = []

            # Early game priority (most important!)
            if "early_game_priority" in tips:
                sections.append("## 🎯 EARLY GAME PRIORITY:")
                for step in tips["early_game_priority"][:5]:  # First 5 steps
                    sections.append(f"  {step}")

            # First hour timeline
            if "first_hour_timeline" in tips:
                sections.append("\n## ⏱️ TIMELINE:")
                for phase, desc in tips["first_hour_timeline"].items():
                    sections.append(f"  - {phase}: {desc}")

            # Starter setups
            if "starter_setups" in tips:
                sections.append("\n## 🔧 QUICK SETUPS:")
                for name, desc in tips["starter_setups"].items():
                    sections.append(f"  - {name}: {desc}")

            # Key ratios
            if "miner_counts_to_fill_belt" in tips:
                electric = tips["miner_counts_to_fill_belt"].get("electric_mining_drill", {})
                sections.append("\n## 📊 KEY RATIOS:")
                sections.append("  - 30 Electric Drills = 1 full yellow belt")
                sections.append("  - 47 Stone Furnaces = 1 full yellow belt of plates")
                sections.append("  - 1 Boiler : 2 Steam Engines")

            return "\n".join(sections)
        except Exception as e:
            print(f"Warning: Could not load strategy tips: {e}")
            return ""

    def _generate_free_exploration(self, observation: StepResult) -> str:
        """Generate code for free exploration after curriculum is done."""

        # Target is chosen by the agent logic, here hardcoded for the demo
        target = "burner-mining-drill"
        recipe_book = self._load_recipes(target)

        skills_context = f"""
# AVAILABLE SKILLS (MACROS):
# Use ONLY strings for arguments!
# - gather('stone', 5)
# - craft('furnace', 1)
# - place('furnace')
# - smelt('iron_ore', 'iron_plate', 5)

{recipe_book}

# RULE 1: Use STRINGS for names. "furnace", "stone", "iron_ore".
# RULE 2: Correct Plan = Check dependencies recursively.
"""

        user_message = f"""
Output: {observation.stdout[-2000:] if observation.stdout else "Ready"}
Error: {observation.stderr[-500:] if observation.stderr else "None"}

{skills_context}

OBJECTIVE: BUILD AUTOMATION
Target: {target} (and placing it on Iron Ore).

PLAN (VETERAN):
1. Check Formula for {target}.
2. Check Ingredients for ingredients recursively.
3. Calculate Totals.
4. Execute Plan using Macros.

Examples of correct planning:
- Need 1 Drill? Drill needs 3 Plates + 3 Gears + 1 Furnace.
- Gears need Plates.
- Plates need Ore + Furnace to smelt.
- So we need SECOND Furnace (one to smelt, one as ingredient).

Generate code. USE ONLY THE MACROS. NO `Prototype` imports.
"""

        code = generate_completion(
            system_prompt=self.get_system_prompt(),
            user_message=user_message,
            max_tokens=1000,
        )

        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()

        return code

    def wrap_code_with_skills(self, code: str) -> str:
        """Inject skills/imports into the code to make it executable."""
        # Inject skills source code directly
        skills_path = Path(__file__).parent.parent / "skills" / "library.py"
        skills_code = ""
        try:
            if skills_path.exists():
                with open(skills_path, "r") as f:
                    skills_code = f.read()
            else:
                print(f"Warning: Skills file not found at {skills_path}")
        except Exception as e:
            print(f"Warning: Could not read skills file: {e}")

        # Combine cleanly
        return skills_code + "\n\n# --- END OF SKILLS ---\n\n" + code

    def process_step_result(self, code: str, obs: StepResult) -> bool:
        """Process the result of a step execution: check success, update KB."""
        metrics = {}

        # Check for errors in BOTH stderr AND stdout
        has_stderr_error = bool(obs.stderr)
        has_stdout_error = obs.stdout and (
            "Error occurred" in obs.stdout or "Exception:" in obs.stdout
        )
        success = not has_stderr_error and not has_stdout_error

        if on_error := (obs.stderr or (obs.stdout if has_stdout_error else None)):
            # Error will be shown by dashboard, no need to print here
            pass

        # Check for tutorial completion - ONLY if truly successful
        if success and self.kb.get_next_tutorial_step():
            self.kb.mark_tutorial_step_complete()

        # Record for curriculum
        self.kb.record_experiment(
            pattern=code[:100],
            success=success,
            phase=self.kb.knowledge["current_phase"],
            metrics=metrics,
            error=on_error[:100] if on_error else None,
        )

        # Track in memory
        result_icon = "✅" if success else f"❌ {obs.stderr[:60]}"
        self.memory.append(
            {"code": code, "success": success, "observation": obs, "timestamp": time.time()}
        )

        return success

    def execute_and_learn(self, code: str) -> Tuple[StepResult, bool]:
        """Execute and learn with curriculum tracking (Standalone mode)"""
        print(f"\n💻 Phase {self.kb.knowledge['current_phase']} Action:\n{code}\n")

        wrapped_code = self.wrap_code_with_skills(code)

        # DEBUG: Print first few lines to check indentation
        print(f"DEBUG: Wrapped Code Start:\n{wrapped_code[:200]}...\n")

        obs = self.env.step(wrapped_code)
        success = self.process_step_result(code, obs)

        return obs, success

        print(f"📊 Result: {result}")
        if obs.stdout:
            print(f"📝 Output: {obs.stdout[:200]}")

        # Check if we should advance phase (simplified logic)
        if success and self.kb.knowledge["stats"]["successful"] % 10 == 0:
            print("\n💡 Consider advancing to next phase soon!")

        return obs, success


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:
    print("🏗️  Starting Megabase Self-Learning Agent...")
    print("📚 Loading curriculum knowledge base...")

    kb = MegabaseKnowledgeBase()
    phase = kb.get_current_phase()

    print(f"\n🎯 Current Phase: {kb.knowledge['current_phase']} - {phase['name']}")
    print(f"   Goal: {phase['goal']}")
    print(f"   Metrics: {', '.join(phase['metrics'])}")

    print("\n🔌 Connecting to Factorio...")
    env = FleEnv()
    # Use soft reset to avoid resetting map and kicking connected players
    print("⚠️  Using soft reset to join existing game...")
    obs = env.reset(soft=True)

    # 🎁 Bootstrap: Starter minimal
    print("\n🎁 Checking starter inventory...")
    # On laisse l'agent commencer avec l'inventaire par défaut du scénario.
    # Apprendre à récolter est la première étape du curriculum !
    print("✅ Ready to learn from scratch")

    agent = MegabaseAgent(env, kb)

    print("\n🎯 Starting curriculum learning...")
    print("=" * 60)

    for step in range(100):  # 100 steps pour construire une vraie mini-base
        print(f"\n{'=' * 60}")
        print(f"STEP {step} | Phase {kb.knowledge['current_phase']}: {phase['name']}")
        print(f"{'=' * 60}")

        code = agent.think(obs)
        obs, success = agent.execute_and_learn(code)

        if obs.done:
            print("\n🎉 Episode complete!")
            break

        # Show progress every 5 steps
        if step % 5 == 0 and step > 0:
            stats = kb.knowledge["stats"]
            print(
                f"\n📊 Progress: {stats['successful']}/{stats['total_experiments']} successful ({stats['successful'] / max(1, stats['total_experiments']) * 100:.1f}%)"
            )

    env.close()

    print("\n" + "=" * 60)
    print("📊 CURRICULUM PROGRESS")
    print("=" * 60)
    print(f"Current Phase: {kb.knowledge['current_phase']}")
    print(
        f"Total Patterns Learned: {sum(len(v) for v in kb.knowledge['building_blocks'].values())}"
    )
    print(
        f"Success Rate: {kb.knowledge['stats']['successful'] / max(1, kb.knowledge['stats']['total_experiments']) * 100:.1f}%"
    )
    print(f"Max PS Achieved: {kb.knowledge['stats'].get('max_ps', 0)}")

    print(f"\n✅ Knowledge saved to: {kb.kb_file}")


if __name__ == "__main__":
    main()
