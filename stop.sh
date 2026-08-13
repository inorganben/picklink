#!/usr/bin/env bash

DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$DIR/logs/app.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm -f "$PID_FILE"
        echo "已停止，PID $PID"
        exit 0
    fi
    rm -f "$PID_FILE"
fi
echo "沒有運行中的程序"
