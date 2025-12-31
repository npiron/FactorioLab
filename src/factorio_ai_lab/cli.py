import argparse
from pathlib import Path

from factorio_ai_lab.config import load_config
from factorio_ai_lab.runner import run_episode


def main() -> None:
    parser = argparse.ArgumentParser(prog="falab")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run an episode (fake or real FLE).")
    p_run.add_argument("--config", default="configs/default.yaml", help="Config file path")
    p_run.add_argument(
        "--mode",
        choices=["fake", "fle"],
        default="fake",
        help="Environment mode: 'fake' (no Docker) or 'fle' (real Factorio)",
    )

    args = parser.parse_args()
    cfg = load_config(Path(args.config))

    if args.cmd == "run":
        run_episode(cfg, mode=args.mode)
    else:
        raise SystemExit("Unknown command")
