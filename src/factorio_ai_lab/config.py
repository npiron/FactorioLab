from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RunConfig:
    name: str
    max_steps: int
    seed: int


@dataclass(frozen=True)
class PathsConfig:
    runs_dir: str


@dataclass(frozen=True)
class AgentConfig:
    prompt_path: str


@dataclass(frozen=True)
class AppConfig:
    run: RunConfig
    paths: PathsConfig
    agent: AgentConfig


def _req(d: dict[str, Any], key: str) -> Any:
    if key not in d:
        raise ValueError(f"Missing config key: {key}")
    return d[key]


def load_config(path: Path) -> AppConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    run = _req(raw, "run")
    paths = _req(raw, "paths")
    agent = _req(raw, "agent")

    return AppConfig(
        run=RunConfig(
            name=str(_req(run, "name")),
            max_steps=int(_req(run, "max_steps")),
            seed=int(_req(run, "seed")),
        ),
        paths=PathsConfig(runs_dir=str(_req(paths, "runs_dir"))),
        agent=AgentConfig(prompt_path=str(_req(agent, "prompt_path"))),
    )
