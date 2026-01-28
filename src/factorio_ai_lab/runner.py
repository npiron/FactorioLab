from __future__ import annotations

import json
import time
import warnings
from pathlib import Path
from datetime import datetime

# Suppress gym deprecation warning
warnings.filterwarnings("ignore", message=".*Gym has been unmaintained.*")

from factorio_ai_lab.config import AppConfig
from factorio_ai_lab.env_adapter import BaseEnv, FakeEnv, FleEnv

# Rich for beautiful terminal UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Install 'rich' for better dashboard: pip install rich")


# ============================================================================
# MINIMALIST DASHBOARD WITH RICH
# ============================================================================


class Dashboard:
    """Beautiful minimalist training dashboard using Rich."""

    def __init__(self, run_id: str, max_steps: int = 100):
        self.run_id = run_id
        self.max_steps = max_steps
        self.start_time = time.time()
        self.steps_success = 0
        self.steps_failed = 0
        self.current_step = 0
        self.current_task = ""
        self.last_error = ""
        self.history = []  # Last N steps

        if RICH_AVAILABLE:
            self.console = Console()

    def header(self):
        """Print dashboard header."""
        if RICH_AVAILABLE:
            self.console.print()
            self.console.print(
                Panel.fit(
                    f"[bold blue]🏭 FACTORIO AI LAB[/bold blue]\n"
                    f"[dim]Run:[/dim] {self.run_id}\n"
                    f"[dim]Started:[/dim] {datetime.now().strftime('%H:%M:%S')}",
                    title="[bold]Training Session[/bold]",
                    border_style="blue",
                )
            )
        else:
            print("\n" + "═" * 60)
            print("  🏭 FACTORIO AI LAB - Training Session")
            print(f"  📋 Run: {self.run_id}")
            print("═" * 60)

    def step_start(self, step: int, task_name: str = ""):
        """Log step start."""
        self.current_step = step
        self.current_task = task_name

    def step_result(
        self, success: bool, stdout: str = "", stderr: str = "", code_preview: str = ""
    ):
        """Log step result with minimal info."""
        elapsed = time.time() - self.start_time

        if success:
            self.steps_success += 1
            status = "✅"
        else:
            self.steps_failed += 1
            status = "❌"
            # Extract error
            error_msg = stderr or stdout
            if "Error:" in error_msg:
                self.last_error = error_msg.split("Error:")[-1].strip()[:60]
            elif "Exception" in error_msg:
                self.last_error = error_msg.split("Exception")[-1].strip()[:60]
            else:
                self.last_error = error_msg.strip()[:60]

        # Store in history
        self.history.append(
            {
                "step": self.current_step,
                "task": self.current_task[:30],
                "status": status,
                "time": elapsed,
            }
        )
        # Keep only last 5
        self.history = self.history[-5:]

        # Print compact status line
        total = self.steps_success + self.steps_failed
        rate = self.steps_success / max(1, total) * 100

        if RICH_AVAILABLE:
            # Create compact status table
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column("Step", style="cyan", width=8)
            table.add_column("Task", width=35)
            table.add_column("Status", width=3)
            table.add_column("Score", style="green", width=15)
            table.add_column("Time", style="dim", width=8)

            table.add_row(
                f"[bold]#{self.current_step:02d}[/bold]",
                self.current_task[:35],
                status,
                f"✓{self.steps_success} ✗{self.steps_failed} ({rate:.0f}%)",
                f"{elapsed:.0f}s",
            )
            self.console.print(table)

            if not success and self.last_error:
                self.console.print(f"   [dim red]└─ {self.last_error}[/dim red]")
        else:
            print(
                f"#{self.current_step:02d} │ {status} │ {self.current_task[:30]} │ ✓{self.steps_success} ✗{self.steps_failed} │ {elapsed:.0f}s"
            )
            if not success and self.last_error:
                print(f"     └─ {self.last_error}")

    def progress_bar(self, current: int, total: int):
        """Show progress bar."""
        if RICH_AVAILABLE:
            pct = current / max(1, total) * 100
            filled = int(30 * current / max(1, total))
            bar = "█" * filled + "░" * (30 - filled)
            self.console.print(f"   [cyan][{bar}][/cyan] {pct:.0f}%")

    def summary(self):
        """Print final summary."""
        elapsed = time.time() - self.start_time
        total = self.steps_success + self.steps_failed
        rate = self.steps_success / max(1, total) * 100

        if RICH_AVAILABLE:
            self.console.print()
            summary_table = Table(title="📊 Session Summary", show_header=False, box=None)
            summary_table.add_column("Metric", style="dim")
            summary_table.add_column("Value", style="bold")

            summary_table.add_row("Total Steps", str(total))
            summary_table.add_row("Success", f"[green]{self.steps_success}[/green] ({rate:.0f}%)")
            summary_table.add_row("Failed", f"[red]{self.steps_failed}[/red]")
            summary_table.add_row("Duration", f"{elapsed:.1f}s")

            self.console.print(Panel(summary_table, border_style="green"))
        else:
            print("\n" + "═" * 60)
            print("  📊 SESSION SUMMARY")
            print(f"  ├─ Total Steps: {total}")
            print(f"  ├─ Success: {self.steps_success} ({rate:.0f}%)")
            print(f"  ├─ Failed: {self.steps_failed}")
            print(f"  └─ Duration: {elapsed:.1f}s")
            print("═" * 60 + "\n")


def run_episode(cfg: AppConfig, mode: str = "fake") -> None:
    """Run a single episode with the specified environment mode.

    Args:
        cfg: Application configuration
        mode: Environment mode ('fake' or 'fle')
    """
    runs_dir = Path(cfg.paths.runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)

    run_id = f"{cfg.run.name}-{mode}-{int(time.time())}"
    out = runs_dir / f"{run_id}.jsonl"

    # Initialize dashboard
    dashboard = Dashboard(run_id, cfg.run.max_steps)
    dashboard.header()

    # Valid prompt path?
    prompt = ""
    if cfg.agent.prompt_path and Path(cfg.agent.prompt_path).is_file():
        prompt = Path(cfg.agent.prompt_path).read_text(encoding="utf-8")

    # Create environment based on mode
    env: BaseEnv
    if mode == "fake":
        env = FakeEnv(seed=cfg.run.seed)
    elif mode == "fle":
        env = FleEnv(seed=cfg.run.seed, instance_id=0)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'fake' or 'fle'.")

    console = Console() if RICH_AVAILABLE else None

    # Handle Autonomous Agent (New Architecture)
    if cfg.agent.agent_type == "autonomous":
        if console:
            console.print("🤖 [bold green]Starting Autonomous Agent[/bold green]")
            console.print(f"🎯 Target: [cyan]{cfg.agent.target_milestone}[/cyan]")
        else:
            print(f"🤖 Starting Autonomous Agent | Target: {cfg.agent.target_milestone}")

        from factorio_ai_lab.agents.autonomous_agent import run_autonomous_agent

        try:
            # Connect/Reset
            result = env.reset()
            if result.stderr or result.done:
                print(f"❌ Reset failed: {result.stderr}")
                return

            # Run the agent
            summary = run_autonomous_agent(
                env=env,
                target=cfg.agent.target_milestone,
                max_steps=cfg.run.max_steps,
                verbose=cfg.agent.verbose,
            )

            # Log summary
            with out.open("w", encoding="utf-8") as f:
                f.write(json.dumps(summary, indent=2))

            print(f"\n📁 Log saved: {out}")

        except Exception as e:
            print(f"❌ Autonomous Agent Error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            env.close()
        return

    # Legacy Agent Logic
    try:
        # Reset environment
        result = env.reset()
        if console:
            console.print(
                f"🎮 [bold]Environment:[/bold] {mode.upper()} │ Reset: [green]OK[/green]"
                if not result.stderr
                else f"🎮 Environment: {mode.upper()} │ Reset: [red]FAIL[/red]"
            )
        else:
            print(
                f"🎮 Environment: {mode.upper()} │ Reset: {'OK' if not result.stderr else 'FAIL'}"
            )

        # Check if reset failed
        if result.done or result.stderr:
            print(f"❌ Reset failed: {result.stderr[:100]}")
            return

        # Run episode
        with out.open("w", encoding="utf-8") as f:
            # Initialize MegabaseAgent if needed
            megabase_agent = None
            if mode == "fle" and (
                "megabase" in cfg.run.name.lower() or "fle-test" in cfg.run.name.lower()
            ):
                try:
                    from factorio_ai_lab.agents.megabase_learning_agent import (
                        MegabaseAgent,
                        MegabaseKnowledgeBase,
                    )

                    kb = MegabaseKnowledgeBase()
                    megabase_agent = MegabaseAgent(env, kb)

                    # Show curriculum status
                    tutorial_step = kb.get_next_tutorial_step()
                    if tutorial_step:
                        if console:
                            console.print(
                                f"📚 [bold]Curriculum:[/bold] Step {tutorial_step['order']} - [cyan]{tutorial_step['type']}[/cyan]"
                            )
                        else:
                            print(
                                f"📚 Curriculum: Step {tutorial_step['order']} - {tutorial_step['type']}"
                            )
                    else:
                        if console:
                            console.print(
                                "📚 [bold]Curriculum:[/bold] [green]Complete![/green] Free exploration mode."
                            )
                        else:
                            print("📚 Curriculum: Complete! Free exploration mode.")

                    if console:
                        console.print()  # Blank line before steps
                except Exception as e:
                    print(f"❌ Agent init failed: {e}")
                    import traceback

                    traceback.print_exc()
                    return

            for step in range(cfg.run.max_steps):
                # Get current task name
                task_name = ""
                if megabase_agent:
                    tutorial_step = megabase_agent.kb.get_next_tutorial_step()
                    if tutorial_step:
                        task_name = tutorial_step["type"]
                    else:
                        task_name = "Free Exploration"

                dashboard.step_start(step, task_name)

                # Choose agent based on mode and config
                if mode == "fle":
                    if megabase_agent:
                        raw_code = megabase_agent.think(result)
                        code = megabase_agent.wrap_code_with_skills(raw_code)
                    elif "starter" in cfg.run.name.lower():
                        from factorio_ai_lab.starter_agent import get_starter_code

                        code = get_starter_code(step)
                        raw_code = code
                    elif "production" in cfg.run.name.lower():
                        from factorio_ai_lab.production_agent import get_production_code

                        code = get_production_code(step)
                        raw_code = code
                    else:
                        from factorio_ai_lab.demo_agent import get_demo_code

                        code = get_demo_code(step)
                        raw_code = code
                else:
                    code = f'print("Step {step}")'
                    raw_code = code

                # Execute step
                result = env.step(code)

                # Determine success
                has_stderr = bool(result.stderr)
                has_stdout_error = result.stdout and (
                    "Error occurred" in result.stdout or "Exception:" in result.stdout
                )
                success = not has_stderr and not has_stdout_error

                # Update Megabase Agent (Learn)
                if megabase_agent:
                    megabase_agent.process_step_result(raw_code, result)

                # Dashboard update
                dashboard.step_result(success, result.stdout, result.stderr, raw_code[:50])

                # Log to JSONL (silent)
                log_entry = {
                    "step": step,
                    "code": code,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "reward": result.reward,
                    "info": result.info,
                    "done": result.done,
                }
                f.write(json.dumps(log_entry) + "\n")

                if result.done:
                    if console:
                        console.print(f"\n🏁 [bold]Episode ended at step {step}[/bold]")
                    else:
                        print(f"\n🏁 Episode ended at step {step}")
                    break

        # Final summary
        dashboard.summary()
        if console:
            console.print(f"📁 Log saved: [dim]{out}[/dim]")
        else:
            print(f"📁 Log saved: {out}")

    finally:
        env.close()


# Legacy function for backward compatibility
def run_smoke(cfg: AppConfig) -> None:
    """Run smoke test (legacy, redirects to fake mode)."""
    run_episode(cfg, mode="fake")
