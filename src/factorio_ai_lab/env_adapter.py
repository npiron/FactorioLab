from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class StepResult:
    """Result of a single environment step."""

    stdout: str
    stderr: str
    reward: float
    info: dict[str, Any]
    done: bool = False


class BaseEnv(Protocol):
    """Protocol for Factorio environments."""

    def reset(self) -> StepResult:
        """Reset the environment to initial state."""
        ...

    def step(self, code: str) -> StepResult:
        """Execute Python code and return result."""
        ...

    def close(self) -> None:
        """Clean up environment resources."""
        ...


class FakeEnv:
    """Fake environment for testing without Factorio."""

    def __init__(self, seed: int = 0):
        self.seed = seed
        self.step_count = 0
        self.max_steps = 50

    def reset(self) -> StepResult:
        """Reset fake environment."""
        self.step_count = 0
        return StepResult(
            stdout="[FakeEnv] Environment reset successfully",
            stderr="",
            reward=0.0,
            info={"seed": self.seed, "mode": "fake"},
            done=False,
        )

    def step(self, code: str) -> StepResult:
        """Simulate executing code."""
        self.step_count += 1

        # Simulate some basic responses
        if "print" in code:
            stdout = f"[FakeEnv] Executed: {code[:50]}..."
        else:
            stdout = f"[FakeEnv] Step {self.step_count} executed"

        # Simulate progressive reward
        reward = float(self.step_count) * 0.1

        # Simulate some fake metrics
        info = {
            "step": self.step_count,
            "ps": self.step_count * 10.0,  # Fake Production Score
            "milestones": {"iron-plate": self.step_count // 5},
            "mode": "fake",
        }

        done = self.step_count >= self.max_steps

        return StepResult(
            stdout=stdout,
            stderr="",
            reward=reward,
            info=info,
            done=done,
        )

    def close(self) -> None:
        """Clean up fake environment."""
        pass


class FleEnv:
    """Real FLE environment (requires Docker + Factorio)."""

    def __init__(self, seed: int = 0, instance_id: int = 0):
        self.seed = seed
        self.instance_id = instance_id
        self.step_count = 0

        # Try to import FLE
        try:
            from fle import Instance  # type: ignore

            self.Instance = Instance
            self.instance: Any = None
        except ImportError as e:
            raise RuntimeError(
                "FLE package not found. Install with: pip install factorio-learning-environment[eval]"
            ) from e

    def reset(self) -> StepResult:
        """Reset FLE environment."""
        try:
            # Initialize FLE instance if not already done
            if self.instance is None:
                self.instance = self.Instance(
                    address=f"localhost:{27015 + self.instance_id}",
                    tcp_port=27015 + self.instance_id,
                    fast=True,
                )

            # Reset the instance
            obs = self.instance.reset()
            self.step_count = 0

            return StepResult(
                stdout=f"[FleEnv] Reset successful: {obs}",
                stderr="",
                reward=0.0,
                info={"seed": self.seed, "mode": "fle", "instance_id": self.instance_id},
                done=False,
            )
        except Exception as e:
            return StepResult(
                stdout="",
                stderr=f"[FleEnv] Reset error: {e}",
                reward=0.0,
                info={"error": str(e)},
                done=True,
            )

    def step(self, code: str) -> StepResult:
        """Execute code in FLE environment."""
        if self.instance is None:
            return StepResult(
                stdout="",
                stderr="[FleEnv] Environment not initialized. Call reset() first.",
                reward=0.0,
                info={"error": "not_initialized"},
                done=True,
            )

        try:
            # Execute code via FLE REPL
            response = self.instance.step(code)
            self.step_count += 1

            # Parse FLE response
            stdout = response.get("stdout", "")
            stderr = response.get("stderr", "")
            reward = response.get("reward", 0.0)

            # Extract metrics if available
            info = {
                "step": self.step_count,
                "mode": "fle",
                "instance_id": self.instance_id,
            }

            if "production_score" in response:
                info["ps"] = response["production_score"]
            if "milestones" in response:
                info["milestones"] = response["milestones"]

            done = response.get("done", False)

            return StepResult(stdout=stdout, stderr=stderr, reward=reward, info=info, done=done)
        except Exception as e:
            return StepResult(
                stdout="",
                stderr=f"[FleEnv] Step error: {e}",
                reward=0.0,
                info={"error": str(e), "step": self.step_count},
                done=True,
            )

    def close(self) -> None:
        """Clean up FLE environment."""
        if self.instance is not None:
            try:
                self.instance.close()
            except Exception:
                pass
            self.instance = None
