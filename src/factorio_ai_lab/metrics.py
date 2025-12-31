from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Metrics:
    step: int
    reward: float = 0.0
    ps: float | None = None
    milestones: dict[str, int] | None = None
