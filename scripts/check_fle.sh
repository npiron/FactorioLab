#!/usr/bin/env bash
set -euo pipefail

# Lance le check cross-platform via Python (plus fiable que timeout/grep selon OS).
python scripts/check_fle.py
