#!/usr/bin/env bash
set -e

# 如果用 sh 运行，自动切换到 bash
if [ -z "$BASH_VERSION" ]; then
    exec bash "$0" "$@"
fi

# ============================================================
# OpenMOSS 一键启动脚本
# 自动完成：检查环境 → 创建 venv → 安装依赖 → 启动服务
# ============================================================

OPENMOSS_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$OPENMOSS_DIR/.venv"
PID_FILE="$OPENMOSS_DIR/.openmoss.pid"
LOG_DIR="$OPENMOSS_DIR/logs"
PORT="${OPENMOSS_PORT:-6565}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

info()  { printf "${GREEN}[OpenMOSS]${NC} %s\n" "$1"; }
warn()  { printf "${YELLOW}[OpenMOSS]${NC} %s\n" "$1"; }
error() { printf "${RED}[OpenMOSS]${NC} %s\n" "$1" >&2; }

echo ""
printf "${BOLD}  🌿 OpenMOSS — 可让多 Agent 自主运行的 AI 公司操作系统${NC}\n"
echo ""

# ---------- 检查是否已在运行 ----------
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        warn "OpenMOSS 已在运行 (PID: $OLD_PID, 端口: $PORT)"
        warn "如需重启，请先执行 ./stop.sh"
        exit 0
    fi
    rm -f "$PID_FILE"
fi

# ============================================================
# Step 1: 检查 Python 3.10+
# ============================================================
find_python() {
    for cmd in python3.13 python3.12 python3.11 python3.10 python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            local ver
            ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null) || continue
            local major minor
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON=$(find_python) || {
    error "❌ 未找到 Python 3.10+"
    echo ""
    echo "  请先安装 Python 3.10 或更高版本："
    echo ""
    echo "  macOS:    brew install python@3.12"
    echo "  Ubuntu:   sudo apt update && sudo apt install python3.12 python3.12-venv"
    echo "  Debian:   sudo apt update && sudo apt install python3.11 python3.11-venv"
    echo "  CentOS:   sudo dnf install python3.12"
    echo "  Arch:     sudo pacman -S python"
    echo ""
    echo "  安装后重新运行: ./start.sh"
    exit 1
}

info "Python: $($PYTHON --version) ($(command -v "$PYTHON"))"

# ============================================================
# Step 2: 检查 venv 模块可用
# ============================================================
if ! $PYTHON -c "import venv" 2>/dev/null; then
    error "❌ Python venv 模块不可用"
    echo ""
    echo "  请安装 venv 模块："
    echo ""
    PYVER=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "  Ubuntu/Debian:  sudo apt install python${PYVER}-venv"
    echo "  CentOS/RHEL:    sudo dnf install python${PYVER}-libs"
    echo ""
    echo "  安装后重新运行: ./start.sh"
    exit 1
fi

# ============================================================
# Step 3: 创建虚拟环境（仅首次）
# ============================================================
if [ ! -d "$VENV_DIR" ]; then
    info "创建虚拟环境..."
    $PYTHON -m venv "$VENV_DIR" || {
        error "❌ 创建虚拟环境失败"
        echo "  请检查 Python 安装是否完整，或尝试手动创建："
        echo "  $PYTHON -m venv $VENV_DIR"
        exit 1
    }
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# ============================================================
# Step 4: 安装/更新依赖（用 hash 跳过重复安装）
# ============================================================
compute_hash() {
    if command -v md5sum >/dev/null 2>&1; then
        md5sum "$1" | cut -d' ' -f1
    elif command -v md5 >/dev/null 2>&1; then
        md5 -q "$1"
    else
        cksum "$1" | cut -d' ' -f1
    fi
}

REQ_FILE="$OPENMOSS_DIR/requirements.txt"
if [ ! -f "$REQ_FILE" ]; then
    error "❌ 未找到 requirements.txt"
    echo "  请确认在 OpenMOSS 项目目录中运行此脚本"
    exit 1
fi

REQ_HASH=$(compute_hash "$REQ_FILE")
OLD_HASH=""
[ -f "$VENV_DIR/.req_hash" ] && OLD_HASH=$(cat "$VENV_DIR/.req_hash")

if [ "$REQ_HASH" != "$OLD_HASH" ]; then
    info "安装 Python 依赖（首次约 30 秒）..."
    pip install --quiet --disable-pip-version-check -r "$REQ_FILE" || {
        error "❌ 依赖安装失败"
        echo "  可能原因："
        echo "  - 网络问题（尝试设置 pip 镜像源）"
        echo "  - 磁盘空间不足"
        echo ""
        echo "  手动安装: source .venv/bin/activate && pip install -r requirements.txt"
        exit 1
    }
    echo "$REQ_HASH" > "$VENV_DIR/.req_hash"
    info "依赖安装完成 ✓"
else
    info "依赖已是最新 ✓"
fi

# ============================================================
# Step 5: 检查前端是否存在
# ============================================================
if [ ! -d "$OPENMOSS_DIR/static" ] || [ ! -f "$OPENMOSS_DIR/static/index.html" ]; then
    info "📦 首次启动，WebUI 前端将在服务启动时自动从 GitHub Release 下载"
fi

# ============================================================
# Step 6: 启动服务
# ============================================================
mkdir -p "$LOG_DIR" "$OPENMOSS_DIR/data"

cd "$OPENMOSS_DIR"


# 用 setsid 启动，使 uvicorn 脱离当前进程组
# 这样 Ctrl+C 或关闭终端不会杀死服务
if command -v setsid >/dev/null 2>&1; then
    setsid "$VENV_DIR/bin/python" -m uvicorn app.main:app \
        --host 0.0.0.0 --port "$PORT" \
        > "$LOG_DIR/server.log" 2>&1 &
else
    nohup "$VENV_DIR/bin/python" -m uvicorn app.main:app \
        --host 0.0.0.0 --port "$PORT" \
        > "$LOG_DIR/server.log" 2>&1 &
fi

SERVER_PID=$!
disown $SERVER_PID 2>/dev/null || true
echo $SERVER_PID > "$PID_FILE"

# ---------- 检查端口是否就绪 ----------
check_port() {
    # 方法 1: bash /dev/tcp（最可靠）
    (echo > /dev/tcp/127.0.0.1/$PORT) 2>/dev/null && return 0
    # 方法 2: curl（跳过代理）
    curl -sf --noproxy '*' --connect-timeout 1 --max-time 2 "http://127.0.0.1:$PORT/api/health" > /dev/null 2>&1 && return 0
    # 方法 3: ss/netstat
    ss -tlnp 2>/dev/null | grep -q ":$PORT " && return 0
    return 1
}

printf "  等待服务启动"
for i in $(seq 1 15); do
    # 先检查进程是否还活着
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo ""
        error "❌ 服务进程已退出"
        echo ""
        echo "  最近日志："
        tail -20 "$LOG_DIR/server.log" 2>/dev/null || true
        echo ""
        echo "  完整日志: $LOG_DIR/server.log"
        rm -f "$PID_FILE"
        exit 1
    fi

    # 检查端口是否就绪
    if check_port; then
        echo ""
        echo ""
        info "✅ OpenMOSS 已启动！"
        echo ""
        echo "  🌐 访问地址:   http://localhost:$PORT"
        echo "  📋 API 文档:   http://localhost:$PORT/docs"
        echo "  📁 日志文件:   $LOG_DIR/server.log"
        echo "  🛑 停止服务:   ./stop.sh"
        echo ""
        info "首次访问会自动跳转到初始化向导 🧙"
        echo ""
        exit 0
    fi
    printf "."
    sleep 1
done

# 15 秒后进程还活着就算成功（可能启动慢）
echo ""
if kill -0 "$SERVER_PID" 2>/dev/null; then
    echo ""
    info "✅ OpenMOSS 已在后台启动 (PID: $SERVER_PID)"
    echo ""
    echo "  🌐 访问地址:   http://localhost:$PORT"
    echo "  📋 API 文档:   http://localhost:$PORT/docs"
    echo "  📁 日志文件:   $LOG_DIR/server.log"
    echo "  🛑 停止服务:   ./stop.sh"
    echo ""
    info "如果无法访问，请稍等几秒或查看日志: tail -f $LOG_DIR/server.log"
    echo ""
else
    error "❌ 服务进程已退出"
    echo ""
    echo "  最近日志："
    tail -20 "$LOG_DIR/server.log" 2>/dev/null || true
    echo ""
    echo "  常见原因："
    echo "  - 端口 $PORT 被占用（尝试: OPENMOSS_PORT=6566 ./start.sh）"
    echo "  - Python 依赖版本冲突"
    rm -f "$PID_FILE"
    exit 1
fi
