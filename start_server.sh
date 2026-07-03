#!/data/data/com.termux/files/usr/bin/bash
# start_server.sh — Decoupled runner for SutraAgent Web Server
termux-wake-lock
pkill -9 -f sutralang_server.py || true
cd /data/data/com.termux/files/home/sutralang
nohup python sutralang_server.py > /data/data/com.termux/files/home/sutra_server.log 2>&1 &
echo "Server started successfully in background with termux-wake-lock active."
