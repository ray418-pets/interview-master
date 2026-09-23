#!/usr/bin/env bash
# 启动服务（FastAPI + uvicorn，同时托管前端静态文件）
# 前后端已联动为单服务：/api 走后端接口，其余路径走前端静态文件
# 用法：bash scripts/start_backend.sh
set -e
cd "$(dirname "$0")/../backend"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "启动服务：http://localhost:${PORT}  (Ctrl+C 停止)"
echo "浏览器打开 http://localhost:${PORT}/ 即可使用（前端 + 后端同源联动）"
exec .venv/Scripts/python.exe -m uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
