#!/bin/bash
# Start the Research Assistant API server
cd "$(dirname "$0")"
source .venv/Scripts/activate 2>/dev/null || source lc-academy-env/Scripts/activate 2>/dev/null || true
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload