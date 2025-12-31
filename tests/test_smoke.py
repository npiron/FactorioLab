from pathlib import Path

from factorio_ai_lab.config import load_config
from factorio_ai_lab.runner import run_smoke


def test_smoke_creates_run_file(tmp_path: Path) -> None:
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(
        """
run:
  name: "test"
  max_steps: 3
  seed: 1
paths:
  runs_dir: "runs"
agent:
  prompt_path: "src/factorio_ai_lab/prompts/early_bootstrap.txt"
""".strip()
    )

    cfg = load_config(cfg_path)
    # point runs_dir vers tmp
    cfg = cfg.__class__(
        run=cfg.run,
        paths=cfg.paths.__class__(runs_dir=str(tmp_path / "runs")),
        agent=cfg.agent,
    )

    run_smoke(cfg)
    assert (tmp_path / "runs").exists()
