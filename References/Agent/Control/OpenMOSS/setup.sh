#!/usr/bin/env bash
set -e

# 如果用 sh 运行，自动切换到 bash
if [ -z "$BASH_VERSION" ]; then
    exec bash "$0" "$@"
fi

# ============================================================
# OpenMOSS 一键安装 / 一键更新脚本
#
# 安装: curl -fsSL https://raw.githubusercontent.com/uluckyXH/OpenMOSS/main/setup.sh | bash
# 更新: 再执行一次同样的命令即可
# ============================================================

REPO="uluckyXH/OpenMOSS"
DOWNLOAD_URL="https://github.com/$REPO/archive/refs/heads/main.tar.gz"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

info() { printf "${GREEN}[OpenMOSS]${NC} %s\n" "$1"; }
warn() { printf "${YELLOW}[OpenMOSS]${NC} %s\n" "$1"; }
error() { printf "${RED}[OpenMOSS]${NC} %s\n" "$1" >&2; }

echo ""
printf "${BOLD}  ╔══════════════════════════════════════════════════════════╗${NC}\n"
printf "${BOLD}  ║   🌿 OpenMOSS 一键安装 / 更新                            ║${NC}\n"
printf "${BOLD}  ║   可让多 Agent 自主运行的 AI 公司操作系统                  ║${NC}\n"
printf "${BOLD}  ╚══════════════════════════════════════════════════════════╝${NC}\n"
echo ""

# ---------- 检查 curl ----------
if ! command -v curl >/dev/null 2>&1; then
    error "需要 curl，请先安装"
    echo "  Ubuntu: sudo apt install curl"
    echo "  CentOS: sudo yum install curl"
    exit 1
fi

# ---------- 判断安装目录：当前目录 or ./openmoss/ ----------
if [ -d "./app" ] && [ -f "./start.sh" ]; then
    # 已经在 openmoss 目录内
    INSTALL_DIR="."
elif [ -d "./openmoss/app" ] && [ -f "./openmoss/start.sh" ]; then
    # 在上层目录，openmoss 是子目录
    INSTALL_DIR="./openmoss"
else
    # 首次安装
    INSTALL_DIR="${OPENMOSS_DIR:-./openmoss}"
fi

# ---------- 判断：首次安装 or 更新 ----------
IS_UPDATE=false
if [ -d "$INSTALL_DIR/app" ] && [ -f "$INSTALL_DIR/start.sh" ]; then
    IS_UPDATE=true
    info "检测到已有安装 ($INSTALL_DIR)，执行更新..."

    # 如果服务正在运行，先停掉
    if [ -f "$INSTALL_DIR/.openmoss.pid" ]; then
        OLD_PID=$(cat "$INSTALL_DIR/.openmoss.pid")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            info "停止运行中的服务 (PID: $OLD_PID)..."
            kill "$OLD_PID" 2>/dev/null || true
            sleep 2
        fi
        rm -f "$INSTALL_DIR/.openmoss.pid"
    fi
else
    info "首次安装..."
fi

# ---------- 下载最新代码 ----------
info "下载最新版本..."
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

curl -fsSL "$DOWNLOAD_URL" -o "$TEMP_DIR/openmoss.tar.gz"
tar xzf "$TEMP_DIR/openmoss.tar.gz" -C "$TEMP_DIR"

SOURCE_DIR="$TEMP_DIR/OpenMOSS-main"

if [ ! -d "$SOURCE_DIR/app" ]; then
    error "下载失败：包内容不完整"
    exit 1
fi

info "下载完成 ✓"

# ---------- 覆盖/安装代码（保留用户数据）----------
mkdir -p "$INSTALL_DIR"

# 需要更新的目录和文件（代码部分）
# 注：static/ (WebUI 前端) 由后端服务启动时自动从 GitHub Release 拉取，不再随主程序分发
for item in app prompts skills rules; do
    if [ -d "$SOURCE_DIR/$item" ]; then
        rm -rf "$INSTALL_DIR/$item"
        cp -r "$SOURCE_DIR/$item" "$INSTALL_DIR/$item"
    fi
done

# 需要更新的文件
for file in requirements.txt config.example.yaml start.sh stop.sh LICENSE; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        cp "$SOURCE_DIR/$file" "$INSTALL_DIR/$file"
    fi
done

chmod +x "$INSTALL_DIR/start.sh" "$INSTALL_DIR/stop.sh" 2>/dev/null || true

# 这些不覆盖（用户数据）：
#   data/         → 数据库
#   config.yaml   → 用户配置
#   .venv/        → Python 虚拟环境（start.sh 会按需更新依赖）
#   logs/         → 日志
#   workspace/    → Agent 工作目录

if [ "$IS_UPDATE" = true ]; then
    info "✅ 代码更新完成（数据和配置已保留）"
else
    info "✅ 安装完成"
fi

# ---------- 启动服务 ----------
echo ""
info "启动服务..."
cd "$INSTALL_DIR"
exec ./start.sh
