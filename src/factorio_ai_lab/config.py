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
    # Legacy field (for old configs)
    prompt_path: str = ""

    # New autonomous agent fields
    agent_type: str = "legacy"  # "legacy", "autonomous"
    target_milestone: str = "craft_burner_drill"
    verbose: bool = True


@dataclass(frozen=True)
class AppConfig:
    run: RunConfig
    paths: PathsConfig
    agent: AgentConfig


def _req(d: dict[str, Any], key: str) -> Any:
    if key not in d:
        raise ValueError(f"Missing config key: {key}")
    return d[key]


def _opt(d: dict[str, Any], key: str, default: Any) -> Any:
    return d.get(key, default)


def load_config(path: Path) -> AppConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    run = _req(raw, "run")
    paths = _req(raw, "paths")
    agent = raw.get("agent", {})

    # Handle both old and new config formats
    agent_type = _opt(agent, "type", "legacy")

    return AppConfig(
        run=RunConfig(
            name=str(_req(run, "name")),
            max_steps=int(_req(run, "max_steps")),
            seed=int(_req(run, "seed")),
        ),
        paths=PathsConfig(runs_dir=str(_req(paths, "runs_dir"))),
        agent=AgentConfig(
            prompt_path=_opt(agent, "prompt_path", ""),
            agent_type=agent_type,
            target_milestone=_opt(agent, "target_milestone", "craft_burner_drill"),
            verbose=_opt(agent, "verbose", True),
        ),
    )
