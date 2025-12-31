import argparse
from pathlib import Path

from factorio_ai_lab.config import load_config
from factorio_ai_lab.runner import run_smoke


def main() -> None:
    parser = argparse.ArgumentParser(prog="falab")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run a local smoke episode (no Factorio required).")
    p_run.add_argument("--config", default="configs/default.yaml")

    args = parser.parse_args()
    cfg = load_config(Path(args.config))

    if args.cmd == "run":
        run_smoke(cfg)
    else:
        raise SystemExit("Unknown command")
