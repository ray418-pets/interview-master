#!/usr/bin/env bash
# 启动后端服务（FastAPI + uvicorn）
# 用法：bash scripts/start_backend.sh
set -e
cd "$(dirname "$0")/../backend"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "启动后端：http://localhost:${PORT}  (Ctrl+C 停止)"
exec .venv/Scripts/python.exe -m uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
