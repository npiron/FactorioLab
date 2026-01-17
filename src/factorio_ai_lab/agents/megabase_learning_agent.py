"""
Megabase Self-Learning Agent
Combines knowledge base with curriculum learning for megabase construction
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from openai import OpenAI
from dotenv import load_dotenv
from factorio_ai_lab.env_adapter import FleEnv, StepResult

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

        return f"""{megabase_prompt}

{goal}

## CURRENT STATUS

🎯 **Current Phase: {self.kb.knowledge["current_phase"]} - {phase["name"]}**

📊 **Progress**:
- Total Experiments: {self.kb.knowledge["stats"]["total_experiments"]}
- Success Rate: {self.kb.knowledge["stats"]["successful"] / max(1, self.kb.knowledge["stats"]["total_experiments"]) * 100:.1f}%
- Guide Progress: {len(learned_types)}/{len(guide_patterns)} étapes

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
        """Generate next action with curriculum awareness"""

        recent = (
            "\n".join(
                [
                    f"Step {i}: {'✅' if m['success'] else '❌'} {m.get('action', 'unknown')[:50]}"
                    for i, m in enumerate(self.memory[-3:])
                ]
            )
            if self.memory
            else "Starting phase " + str(self.kb.knowledge["current_phase"])
        )

        user_message = f"""
Recent steps:
{recent}

Output: {observation.stdout[-300:] if observation.stdout else "Ready"}
Error: {observation.stderr[-200:] if observation.stderr else "None"}

What's the next step towards the phase goal? 
Generate Python code only. Focus on {self.kb.get_current_phase()["goal"]}.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=cast(
                Any,
                [
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": user_message},
                ],
            ),
            max_tokens=600,
            temperature=0.5,
        )

        code = response.choices[0].message.content or ""

        # Extract code
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()

        return code

    def execute_and_learn(self, code: str) -> Tuple[StepResult, bool]:
        """Execute and learn with curriculum tracking"""
        print(f"\n💻 Phase {self.kb.knowledge['current_phase']} Action:\n{code}\n")

        obs = self.env.step(code)
        success = not obs.stderr

        # Extract metrics if available
        metrics = {}
        if hasattr(obs, "reward"):
            metrics["reward"] = obs.reward

        # Record for curriculum
        self.kb.record_experiment(
            pattern=code[:100],
            success=success,
            phase=self.kb.knowledge["current_phase"],
            metrics=metrics,
            error=obs.stderr[:100] if obs.stderr else None,
        )

        # Track in memory
        result = "✅" if success else f"❌ {obs.stderr[:60]}"
        self.memory.append(
            {
                "code": code[:50],
                "result": result,
                "success": success,
                "action": code.split("\n")[0] if code else "unknown",
            }
        )

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
