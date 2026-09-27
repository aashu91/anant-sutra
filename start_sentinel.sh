#!/data/data/com.termux/files/usr/bin/env bash
# start_sentinel.sh — Controls background execution of 24/7 SutraOS Sentinel

SCRIPT_DIR="/data/data/com.termux/files/home/sutralang"
DAEMON_SCRIPT="$SCRIPT_DIR/sutra_sentinel_daemon.py"
LOG_FILE="$SCRIPT_DIR/sentinel_daemon.log"

case "$1" in
    start)
        if pgrep -f "sutra_sentinel_daemon.py" > /dev/null; then
            echo "[INFO] SutraOS Sentinel is ALREADY running."
        else
            echo "[START] Launching 24/7 Sovereign Sentinel in background..."
            nohup python3 "$DAEMON_SCRIPT" > "$LOG_FILE" 2>&1 &
            echo "[SUCCESS] Sentinel started! Log file: $LOG_FILE"
        fi
        ;;
    stop)
        echo "[STOP] Terminating SutraOS Sentinel daemon..."
        pkill -f "sutra_sentinel_daemon.py"
        echo "[SUCCESS] Sentinel stopped."
        ;;
    status)
        if pgrep -f "sutra_sentinel_daemon.py" > /dev/null; then
            PID=$(pgrep -f "sutra_sentinel_daemon.py")
            echo "🟢 SutraOS Sentinel is RUNNING (PID: $PID)"
            echo "--- Recent Logs ---"
            tail -n 10 "$LOG_FILE" 2>/dev/null
        else
            echo "🔴 SutraOS Sentinel is STOPPED."
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac
