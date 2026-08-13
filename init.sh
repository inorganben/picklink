#!/usr/bin/env bash
set -e

ENV_NAME="pdf"
PY="/opt/miniconda3/envs/${ENV_NAME}/bin/python"

if [ ! -f "$PY" ]; then
    echo "找不到 conda 環境：${ENV_NAME}"
    exit 1
fi

echo "安裝依賴到 ${ENV_NAME} 環境…"
"$PY" -m pip install --upgrade pip
"$PY" -m pip install PySide6 trafilatura beautifulsoup4 requests python-dotenv playwright

echo "完成。啟動方式：./start.sh（後台）或 ./start.sh dev（前台查看報錯）"
