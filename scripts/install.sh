#!/bin/bash
# ============================================================
# MemoryDay 在线安装引导脚本
# 用法: curl -fsSL https://你的服务器/install.sh | bash
# 或:   wget -qO- https://你的服务器/install.sh | bash
# ============================================================
# 此脚本会检测环境，下载项目并自动部署到 /opt/memoryday
# 支持任意云服务器：腾讯云、阿里云、华为云、AWS、GCP 等
# ============================================================

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║       MemoryDay 在线安装引导脚本 v2.0         ║"
echo "  ║     任意云服务器 | 一键部署 | 开箱即用        ║"
echo "  ╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查 root 权限
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}[ERROR] 请使用 root 用户运行${NC}"
    exit 1
fi

# 检测操作系统
echo -e "${BLUE}[INFO]${NC} 检测系统环境..."
OS=""
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    echo "  系统: $NAME $VERSION"
elif [ -f /etc/opencloudos-release ]; then
    OS="opencloudos"
    echo "  系统: OpenCloudOS"
else
    echo -e "${YELLOW}[WARN]${NC} 无法检测系统类型，假设为 CentOS"
    OS="centos"
fi

# 安装 Git（如果未安装）
if ! command -v git &>/dev/null; then
    echo -e "${BLUE}[INFO]${NC} 安装 Git..."
    case $OS in
        ubuntu|debian) apt-get update -qq && apt-get install -y -qq git ;;
        *) yum install -y git 2>/dev/null || dnf install -y git 2>/dev/null ;;
    esac
fi

# 克隆项目
PROJECT_DIR="/tmp/memoryday-install-$$"
echo -e "${BLUE}[INFO]${NC} 下载 MemoryDay 项目..."
if [ -n "$GIT_REPO" ]; then
    git clone --depth=1 "$GIT_REPO" "$PROJECT_DIR"
else
    # 默认仓库地址，用户可以替换
    GIT_REPO_DEFAULT="https://github.com/your-repo/memoryday.git"
    echo -e "${YELLOW}[!]${NC} 请设置 GIT_REPO 环境变量指定仓库地址"
    echo "  例如: GIT_REPO=https://github.com/user/memoryday.git bash install.sh"
    echo ""
    read -p "请输入 Git 仓库地址 (或直接回车使用默认): " GIT_REPO_INPUT
    GIT_REPO="${GIT_REPO_INPUT:-$GIT_REPO_DEFAULT}"
    git clone --depth=1 "$GIT_REPO" "$PROJECT_DIR"
fi

# 运行部署脚本
cd "$PROJECT_DIR"
chmod +x scripts/deploy.sh

echo ""
echo -e "${CYAN}━━━ 开始部署 MemoryDay ━━━${NC}"
echo ""

# 执行部署
bash scripts/deploy.sh

# 清理临时文件
rm -rf "$PROJECT_DIR" &

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  MemoryDay 部署流程已启动!${NC}"
echo -e "${GREEN}  部署目录: /opt/memoryday${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  查看部署日志: ${BLUE}tail -f /opt/memoryday/backend/logs/django.log${NC}"
echo ""