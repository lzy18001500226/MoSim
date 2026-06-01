#!/usr/bin/env bash

# 如果用 sh 运行，自动切换到 bash
if [ -z "$BASH_VERSION" ]; then
    exec bash "$0" "$@"
fi

# ============================================================
# OpenMOSS 停止脚本
# ============================================================

OPENMOSS_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$OPENMOSS_DIR/.openmoss.pid"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

stop_pid() {
    local pid=$1
    kill "$pid" 2>/dev/null
    # 等待进程退出（最多 5 秒）
    for i in $(seq 1 10); do
        if ! kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
        sleep 0.5
    done
    # 还没退出就强杀
    kill -9 "$pid" 2>/dev/null || true
}

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        stop_pid "$PID"
        printf "${GREEN}[OpenMOSS]${NC} 服务已停止 (PID: %s)\n" "$PID"
    else
        printf "${YELLOW}[OpenMOSS]${NC} 服务未运行 (PID %s 已不存在)\n" "$PID"
    fi
    rm -f "$PID_FILE"
else
    # 没有 PID 文件，通过进程名查找
    PIDS=$(pgrep -f "uvicorn app.main:app" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | while read -r pid; do
            stop_pid "$pid"
        done
        printf "${GREEN}[OpenMOSS]${NC} 服务已停止\n"
    else
        printf "${YELLOW}[OpenMOSS]${NC} 服务未运行\n"
    fi
fi
