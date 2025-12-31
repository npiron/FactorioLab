#!/usr/bin/env python3
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Sequence


@dataclass
class CmdResult:
    cmd: str
    ok: bool
    code: int | None
    stdout: str
    stderr: str
    timed_out: bool = False


def run(cmd: Sequence[str], timeout_s: int = 20) -> CmdResult:
    cmd_str = " ".join(cmd)
    try:
        p = subprocess.run(
            list(cmd),
            text=True,
            capture_output=True,
            timeout=timeout_s,
            check=False,
            env=os.environ.copy(),
        )
        return CmdResult(
            cmd=cmd_str,
            ok=(p.returncode == 0),
            code=p.returncode,
            stdout=p.stdout.strip(),
            stderr=p.stderr.strip(),
            timed_out=False,
        )
    except subprocess.TimeoutExpired as e:
        return CmdResult(
            cmd=cmd_str,
            ok=False,
            code=None,
            stdout=(e.stdout or "").strip(),
            stderr=(e.stderr or "").strip(),
            timed_out=True,
        )


def section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_cmd(res: CmdResult) -> None:
    status = "OK" if res.ok else ("TIMEOUT" if res.timed_out else "KO")
    code = "?" if res.code is None else str(res.code)
    print(f"\n$ {res.cmd}")
    print(f"-> {status} (code={code})")
    if res.stdout:
        print("\n[stdout]")
        print(res.stdout)
    if res.stderr:
        print("\n[stderr]")
        print(res.stderr)


def main() -> int:
    section("Context")
    print(f"Platform: {platform.platform()}")
    print(f"Python:   {sys.version.splitlines()[0]}")
    print(f"Venv:     {os.environ.get('VIRTUAL_ENV', '(none)')}")
    print(f"PWD:      {os.getcwd()}")

    section("A) Discover FLE / Factorio packages")
    res = run([sys.executable, "-m", "pip", "list"])
    # on n'affiche pas toute la liste, on filtre localement
    pkgs = res.stdout.splitlines() if res.stdout else []
    filtered = [line for line in pkgs if any(k in line.lower() for k in ["fle", "factorio"])]
    print("$ python -m pip list | (filtered: fle/factorio)")
    print("-> " + ("FOUND" if filtered else "NOT FOUND"))
    for line in filtered[:50]:
        print(line)
    if res.stderr:
        print("\n[pip stderr]\n" + res.stderr)

    section("B) CLI 'fle' presence")
    fle_path = shutil.which("fle")
    print(f"which fle -> {fle_path or '(not found)'}")

    if fle_path:
        help_res = run(["fle", "--help"], timeout_s=10)
        print_cmd(help_res)

    section("C) Python imports (best-effort)")
    import_check = run(
        [
            sys.executable,
            "-c",
            (
                "import importlib.util;"
                "mods=['fle','factorio_learning_environment','factorio_learn','factorio'];"
                "print({m: (importlib.util.find_spec(m) is not None) for m in mods})"
            ),
        ],
        timeout_s=10,
    )
    print_cmd(import_check)

    section("D) Attempt headless smoke: 'fle cluster start' (timeout 20s)")
    if not fle_path:
        print("SKIP: 'fle' not found. Install/activate FLE first, then re-run this script.")
        print("\nNext actions:")
        print(
            "- Ensure you are in your venv and install FLE (exact package name depends on your setup)."
        )
        print("- Then rerun: python scripts/check_fle.py")
        return 2

    start_res = run(["fle", "cluster", "start"], timeout_s=20)
    print_cmd(start_res)

    # Si 'start' réussit ou timeout, on tente status/stop en best-effort (sans échouer si absent)
    section("E) Best-effort: status / stop (won't fail the script)")
    for cmd in (["fle", "cluster", "status"], ["fle", "cluster", "stop"]):
        res2 = run(cmd, timeout_s=10)
        print_cmd(res2)

    section("Verdict")
    ok_cli = fle_path is not None
    ok_import = "True" in import_check.stdout if import_check.stdout else False

    # start: OK ou TIMEOUT = "probablement lancé", KO = souci
    ok_start = start_res.ok or start_res.timed_out

    print(f"- CLI fle:            {'OK' if ok_cli else 'KO'}")
    print(f"- Python import check: {'OK' if ok_import else 'KO/UNKNOWN'}")
    print(f"- cluster start smoke: {'OK' if ok_start else 'KO'}")

    if ok_cli and ok_start:
        print("\nPASS: FLE semble accessible et un cluster peut être lancé (ou démarre).")
        print("Next: brancher `falab run --mode fle` avec un Env adapter.")
        return 0

    print("\nFAIL: il manque FLE (ou le cluster ne démarre pas).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
