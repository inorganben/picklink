#!/usr/bin/env bash

ENV_NAME="pdf"
PY="/opt/miniconda3/envs/${ENV_NAME}/bin/python"
DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$DIR/logs"
mkdir -p "$LOG_DIR"

if [ "$1" = "dev" ]; then
    echo "dev 模式：前台運行，Ctrl+C 結束"
    exec "$PY" -m app.main
fi

nohup "$PY" -m app.main > "$LOG_DIR/app.log" 2>&1 &
echo $! > "$LOG_DIR/app.pid"
echo "已啟動，PID $(cat "$LOG_DIR/app.pid")，日誌：$LOG_DIR/app.log"
