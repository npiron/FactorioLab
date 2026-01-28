from __future__ import annotations

import warnings

# Suppress gym deprecation warning before importing anything that uses gym
warnings.filterwarnings("ignore", message=".*Gym has been unmaintained.*")

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
        stdout = ""

        # Simple state simulation
        if not hasattr(self, "inventory"):
            self.inventory = {}

        # Parse commands roughly
        if "gather" in code:
            import re

            m = re.search(r"gather\(['\"](\w+)['\"],\s*qty=(\d+)\)", code)
            if not m:
                m = re.search(r"gather\(['\"](\w+)['\"],\s*(\d+)\)", code)
            if m:
                item = m.group(1)
                qty = int(m.group(2))
                self.inventory[item] = self.inventory.get(item, 0) + qty
                stdout += f"🌲 Gathering {qty} {item}...\n"
                stdout += f"✅ Harvested {qty}\n"

        if "craft" in code:
            import re

            m = re.search(r"craft\(['\"](\w+)['\"],\s*(\d+)\)", code)
            if m:
                item = m.group(1)
                qty = int(m.group(2))
                self.inventory[item] = self.inventory.get(item, 0) + qty
                stdout += f"🔨 Crafting {qty} {item}...\n"
                stdout += f"✅ Crafted {qty}\n"

        if "place" in code:
            import re

            m = re.search(r"place\(['\"](\w+)['\"]", code)
            if m:
                item = m.group(1)
                stdout += f"🏗️ Placing {item}...\n"
                stdout += "✅ Placed at Position(x=10, y=10)\n"

        if "check_inventory" in code or "inspect_inventory" in code:
            # Format inventory like real FLE
            inv_str = ", ".join([f"'{k}': {v}" for k, v in self.inventory.items()])
            stdout += f"📦 Inventory: {{{inv_str}}}\n"

        if "smelt" in code:
            import re

            m = re.search(r"smelt\(['\"](\w+)['\"],\s*['\"](\w+)['\"],\s*(\d+)\)", code)
            if m:
                src, dst, qty = m.groups()
                qty = int(qty)
                self.inventory[dst] = self.inventory.get(dst, 0) + qty
                stdout += f"🔥 Smelting {qty} {src} -> {dst}...\n"
                stdout += f"✅ Smelted {qty} {dst}\n"

        # Look for simple print
        if not stdout and "print" in code:
            stdout = f"[FakeEnv] Executed: {code[:50]}..."

        # Fallback
        if not stdout:
            stdout = "[FakeEnv] No output"

        reward = float(self.step_count) * 0.1
        info = {"step": self.step_count, "mode": "fake"}
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
            from fle.env.instance import FactorioInstance

            self.Instance = FactorioInstance
            self.instance: Any = None
        except ImportError as e:
            raise RuntimeError(
                "FLE package not found. Install with: pip install factorio-learning-environment[eval]"
            ) from e

    def reset(self, soft: bool = False) -> StepResult:
        """Reset FLE environment.

        Args:
            soft: If True, only connect without hard resetting the game state.
        """
        try:
            # Initialize FLE instance if not already done
            if self.instance is None:
                # Connect to existing cluster instance
                port = 27000 + self.instance_id
                self.instance = self.Instance(
                    address="localhost",
                    tcp_port=port,
                    fast=True,
                )

            # Reset the instance ONLY if not soft
            if not soft:
                self.instance.reset()
            else:
                print("[FleEnv] Soft reset: Skipping game state reset to preserve connection")

            self.step_count = 0

            return StepResult(
                stdout="[FleEnv] Reset successful (Soft)" if soft else "[FleEnv] Reset successful",
                stderr="",
                reward=0.0,
                info={"seed": self.seed, "mode": "fle", "instance_id": self.instance_id},
                done=False,
            )
        except Exception as e:
            import traceback

            error_detail = traceback.format_exc()
            return StepResult(
                stdout="",
                stderr=f"[FleEnv] Reset error: {e}\n{error_detail}",
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
            response = self.instance.eval(code)
            self.step_count += 1

            # Parse FLE response - adjust based on actual FLE API
            stdout = str(response) if response else ""
            stderr = ""
            reward = 0.0  # FLE doesn't have reward by default

            # Extract metrics if available
            info = {
                "step": self.step_count,
                "mode": "fle",
                "instance_id": self.instance_id,
            }

            done = False

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
