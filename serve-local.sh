#!/usr/bin/env bash
# Local preview for Calixlab Trainer Hub (static + Apps Script stub).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
python3 build_merge.py
PORT="${PORT:-8765}"
echo "Serving http://127.0.0.1:${PORT}/"
echo "  Onboarding opens first. Backend is stubbed (localStorage log)."
echo "  In browser console: calixlabLocalLog()  calixlabClearLocalLog()"
exec python3 -m http.server "$PORT" --bind 127.0.0.1
