from __future__ import annotations

import json
import time
from pathlib import Path

from factorio_ai_lab.config import AppConfig
from factorio_ai_lab.env_adapter import FakeEnv, FleEnv


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

    prompt = Path(cfg.agent.prompt_path).read_text(encoding="utf-8")
    print(f"[falab] run_id={run_id}")
    print(f"[falab] mode={mode}")
    print(f"[falab] loaded prompt: {cfg.agent.prompt_path} ({len(prompt)} chars)")

    # Create environment based on mode
    if mode == "fake":
        env = FakeEnv(seed=cfg.run.seed)
    elif mode == "fle":
        env = FleEnv(seed=cfg.run.seed, instance_id=0)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'fake' or 'fle'.")

    try:
        # Reset environment
        result = env.reset()
        print(f"[falab] reset: {result.stdout[:100]}")

        # Run episode
        with out.open("w", encoding="utf-8") as f:
            for step in range(cfg.run.max_steps):
                # Simple policy: just print step number
                code = f'print("Step {step}")'

                # Execute step
                result = env.step(code)

                # Log to JSONL
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
                    print(f"[falab] episode ended at step {step}")
                    break

        print(f"[falab] wrote: {out}")
    finally:
        env.close()


# Legacy function for backward compatibility
def run_smoke(cfg: AppConfig) -> None:
    """Run smoke test (legacy, redirects to fake mode)."""
    run_episode(cfg, mode="fake")
