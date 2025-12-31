from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

from factorio_ai_lab.config import AppConfig
from factorio_ai_lab.metrics import Metrics


def run_smoke(cfg: AppConfig) -> None:
    runs_dir = Path(cfg.paths.runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)

    run_id = f"{cfg.run.name}-{int(time.time())}"
    out = runs_dir / f"{run_id}.jsonl"

    prompt = Path(cfg.agent.prompt_path).read_text(encoding="utf-8")
    print(f"[falab] run_id={run_id}")
    print(f"[falab] loaded prompt: {cfg.agent.prompt_path} ({len(prompt)} chars)")

    # Ici, plus tard, tu remplaces la boucle par env.step(...) via FLE.
    with out.open("w", encoding="utf-8") as f:
        for step in range(cfg.run.max_steps):
            m = Metrics(step=step, reward=0.0, ps=None, milestones=None)
            f.write(json.dumps(asdict(m)) + "\n")

    print(f"[falab] wrote: {out}")
