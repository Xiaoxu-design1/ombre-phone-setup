#!/bin/bash
# Restart all Ombre Brain services (run inside Ubuntu)
# v2: 5 services (server / ip / vision / chess / hook_bridge)
cd ~/Ombre-Brain

echo "[1/3] stopping old processes..."
pkill -f "src/server.py" 2>/dev/null
pkill -f "ip_mcp.py" 2>/dev/null
pkill -f "vision_mcp.py" 2>/dev/null
pkill -f "chess_mcp.py" 2>/dev/null
pkill -f "hook_bridge.py" 2>/dev/null
sleep 1

echo "[2/3] loading env..."
set -a && . ./.env && set +a

echo "[3/3] starting services..."
nohup python3 src/server.py > ob.log 2>&1 &
nohup python3 ip_mcp.py > ip.log 2>&1 &
nohup python3 vision_mcp.py > vision.log 2>&1 &
nohup python3 chess_mcp.py > chess.log 2>&1 &
nohup python3 hook_bridge.py > bridge.log 2>&1 &

sleep 4
echo "===================="
curl -s http://127.0.0.1:18001/health && echo " <- Ombre Brain OK"
pgrep -f hook_bridge.py >/dev/null && echo "hook bridge OK (port 18005)" || echo "WARNING: hook bridge NOT running!"
echo "===================="
