#!/usr/bin/env bash
# 启动前端静态服务（原生 HTML/CSS/JS，无构建）
# 前端通过 js/config.js 将 API 请求指向后端 http://localhost:8000/api
# 用法：bash scripts/start_frontend.sh
set -e
cd "$(dirname "$0")/../frontend"

PORT="${PORT:-8080}"

echo "启动前端：http://localhost:${PORT}  (Ctrl+C 停止)"
exec ../backend/.venv/Scripts/python.exe -m http.server "$PORT"
