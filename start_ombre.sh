#!/bin/bash
# Ombre Brain 一键启动脚本（在 Ubuntu 里运行）
# 用法：cd ~/Ombre-Brain && bash start_ombre.sh
set -e
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "❌ 没找到 .env，请先：cp env.example .env 并填入你的 Key"
  exit 1
fi

set -a; . ./.env; set +a

echo "🚀 启动 Ombre Brain ..."
echo "   传输方式: $OMBRE_TRANSPORT"
echo "   MCP 地址: http://127.0.0.1:18001/mcp"
echo "   Dashboard: http://127.0.0.1:18001"

exec python3 src/server.py
