#!/usr/bin/env bash
#
# Weather CLI — 一键安装脚本
# Usage: curl -fsSL https://raw.githubusercontent.com/realhenrylan/Weather-Agent-CLI/main/install.sh | bash
#
set -euo pipefail

REPO="https://github.com/realhenrylan/Weather-Agent-CLI.git"
RAW_BASE="https://raw.githubusercontent.com/realhenrylan/Weather-Agent-CLI/main"
APP_NAME="weather-cli"

# ── 颜色 ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { printf "${CYAN}%s${NC}\n" "$*"; }
ok()    { printf "${GREEN}✓ %s${NC}\n" "$*"; }
warn()  { printf "${YELLOW}⚠ %s${NC}\n" "$*"; }
err()   { printf "${RED}✗ %s${NC}\n" "$*"; exit 1; }

# ── 平台检测 ──
OS="$(uname -s)"
case "$OS" in
  Linux)   OS="linux" ;;
  Darwin)  OS="macos" ;;
  MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
  *)       err "不支持的系统: $OS (仅支持 Linux / macOS / Windows Git Bash)" ;;
esac

info "============================================"
info "  Weather CLI 安装程序"
info "  目标系统: $OS"
info "============================================"
echo ""

# ── Python 检测 ──
PYTHON=""
for cmd in python3.12 python3.11 python3.10 python3 python; do
  if command -v "$cmd" &>/dev/null; then
    VER=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0")
    MAJOR=${VER%.*}; MINOR=${VER#*.}
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
      PYTHON="$cmd"
      break
    fi
  fi
done

[ -z "$PYTHON" ] && err "未找到 Python 3.10+。请安装后重试。"
ok "Python $VER ($(command -v "$PYTHON"))"

# ── pip 检测 ──
$PYTHON -m pip --version &>/dev/null || err "pip 未安装。请运行: $PYTHON -m ensurepip --upgrade"
ok "pip 已就绪"

# ── 安装 ──
echo ""
info "正在安装 $APP_NAME ..."

INSTALL_CMD="$PYTHON -m pip install --upgrade git+$REPO"
if [ "$OS" = "windows" ]; then
  warn "Windows 建议在管理员 PowerShell 中运行:"
  warn "  python -m pip install git+$REPO"
fi

if [ "$(id -u)" -ne 0 ]; then
  INSTALL_CMD="$INSTALL_CMD --user"
fi

eval "$INSTALL_CMD" 2>&1 | tail -5
echo ""

# ── 验证 ──
if command -v "$APP_NAME" &>/dev/null; then
  ok "安装成功！运行 weather-cli 启动"
else
  # 尝试为 PATH 添加 ~/.local/bin
  if [ "$OS" != "windows" ]; then
    BIN_DIR="$HOME/.local/bin"
    if [ -f "$BIN_DIR/$APP_NAME" ] && [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
      warn "请将 $BIN_DIR 添加到 PATH:"
      echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
      echo "  source ~/.bashrc"
    fi
  fi
  warn "安装完成，但命令可能不在 PATH 中"
  warn "运行方式: $PYTHON -m weather_cli"
fi

echo ""
info "首次运行会引导你配置 LLM API Key 和和风天气 Key"
info "详情: https://github.com/realhenrylan/Weather-Agent-CLI"
