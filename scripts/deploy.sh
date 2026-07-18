#!/bin/bash
# ============================================================
# MemoryDay 通用一键部署脚本 v2.0
# 支持: OpenCloudOS / CentOS / RHEL / Ubuntu / Debian / Rocky / AlmaLinux
# 功能: 自动安装 Docker + 自动部署 + 环境配置 + 健康检查
# 用法: curl -fsSL https://你的服务器/install.sh | bash
# ============================================================

set -e

# ---------- 颜色定义 ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
log_error()   { echo -e "${RED}[✗]${NC} $1"; }
log_step()    { echo -e "\n${CYAN}━━━ $1 ━━━${NC}"; }

# ---------- 横幅 ----------
show_banner() {
    echo ""
    echo -e "${CYAN}"
    echo "  ╔══════════════════════════════════════════════╗"
    echo "  ║         MemoryDay 通用一键部署脚本 v2.0       ║"
    echo "  ║     Docker 化部署 | 多系统支持 | 开箱即用     ║"
    echo "  ╚══════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ============================================================
# 1. 环境检测
# ============================================================
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "请使用 root 用户或 sudo 提权运行此脚本"
        exit 1
    fi
}

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_ID=$ID
        OS_NAME=$NAME
        OS_VERSION=$VERSION_ID
    elif [ -f /etc/opencloudos-release ]; then
        OS_ID="opencloudos"
        OS_NAME="OpenCloudOS"
        OS_VERSION=$(cat /etc/opencloudos-release | grep -oP '[0-9]+\.[0-9]+' || echo "unknown")
    elif command -v lsb_release &>/dev/null; then
        OS_ID=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
        OS_NAME=$(lsb_release -sd)
        OS_VERSION=$(lsb_release -sr)
    else
        log_error "无法检测操作系统，请手动安装 Docker 后重试"
        exit 1
    fi

    log_info "检测到操作系统: ${OS_NAME} ${OS_VERSION}"

    # 映射到包管理器
    case $OS_ID in
        ubuntu|debian)
            PKG_MANAGER="apt"
            DOCKER_CE_REPO="ubuntu"
            ;;
        centos|rhel|rocky|almalinux|opencloudos|anolis|openeuler)
            PKG_MANAGER="yum"
            DOCKER_CE_REPO="centos"
            ;;
        fedora)
            PKG_MANAGER="dnf"
            DOCKER_CE_REPO="fedora"
            ;;
        *)
            log_error "不支持的操作系统: ${OS_NAME}"
            log_info "支持的发行版: Ubuntu, Debian, CentOS, RHEL, Rocky, AlmaLinux, OpenCloudOS, Fedora"
            exit 1
            ;;
    esac
    log_success "操作系统识别成功: ${OS_NAME} ${OS_VERSION}"
}

check_docker() {
    if command -v docker &>/dev/null; then
        log_success "Docker 已安装 ($(docker --version 2>/dev/null))"
        return 0
    fi
    return 1
}

check_docker_compose() {
    if docker compose version &>/dev/null; then
        DOCKER_COMPOSE="docker compose"
        log_success "Docker Compose 已安装 (插件模式)"
        return 0
    elif command -v docker-compose &>/dev/null; then
        DOCKER_COMPOSE="docker-compose"
        log_success "Docker Compose 已安装 (独立模式)"
        return 0
    fi
    return 1
}

# ============================================================
# 2. 安装 Docker
# ============================================================
install_docker() {
    log_step "安装 Docker 运行时"

    if check_docker && check_docker_compose; then
        log_success "Docker 已就绪，跳过安装"
        return 0
    fi

    log_info "正在安装 Docker..."

    case $PKG_MANAGER in
        apt)
            apt-get update -qq
            apt-get install -y -qq ca-certificates curl gnupg lsb-release
            install -m 0755 -d /etc/apt/keyrings
            # 阿里云镜像加速
            curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/${DOCKER_CE_REPO}/gpg | \
                gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null || \
                curl -fsSL https://download.docker.com/linux/${DOCKER_CE_REPO}/gpg | \
                gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            chmod a+r /etc/apt/keyrings/docker.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/${DOCKER_CE_REPO} $(lsb_release -cs 2>/dev/null || echo 'stable') stable" | \
                tee /etc/apt/sources.list.d/docker.list > /dev/null
            apt-get update -qq
            apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        yum|dnf)
            # 安装依赖
            $PKG_MANAGER install -y yum-utils device-mapper-persistent-data lvm2 2>/dev/null || true
            # 阿里云镜像加速
            yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/${DOCKER_CE_REPO}/docker-ce.repo 2>/dev/null || \
                dnf config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/${DOCKER_CE_REPO}/docker-ce.repo 2>/dev/null || \
                yum-config-manager --add-repo https://download.docker.com/linux/${DOCKER_CE_REPO}/docker-ce.repo
            $PKG_MANAGER install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
    esac

    # 启动 Docker
    systemctl enable docker 2>/dev/null || true
    systemctl start docker 2>/dev/null || true

    # 配置镜像加速
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
    systemctl restart docker 2>/dev/null || true

    # 验证安装
    if check_docker; then
        check_docker_compose
        log_success "Docker 安装成功"
    else
        log_error "Docker 安装失败，请手动安装"
        exit 1
    fi
}

# ============================================================
# 3. 配置防火墙
# ============================================================
config_firewall() {
    log_step "配置防火墙规则"

    local ports="80 443"

    if systemctl is-active firewalld &>/dev/null; then
        for port in $ports; do
            firewall-cmd --permanent --add-port=${port}/tcp &>/dev/null || true
        done
        firewall-cmd --reload &>/dev/null || true
        log_success "firewalld 端口已开放: $(echo $ports | tr ' ' ', ')"
    elif systemctl is-active ufw &>/dev/null; then
        for port in $ports; do
            ufw allow ${port}/tcp &>/dev/null || true
        done
        ufw reload &>/dev/null || true
        log_success "ufw 端口已开放: $(echo $ports | tr ' ' ', ')"
    else
        log_warn "未检测到防火墙，请手动开放端口: $(echo $ports | tr ' ' ', ')"
        # 尝试 iptables
        if command -v iptables &>/dev/null; then
            for port in $ports; do
                iptables -I INPUT -p tcp --dport ${port} -j ACCEPT 2>/dev/null || true
            done
            log_info "已添加 iptables 规则"
        fi
    fi
}

# ============================================================
# 4. 生成随机密码
# ============================================================
gen_pass() {
    openssl rand -base64 24 2>/dev/null | tr -d '/+=' | cut -c1-24 || echo "memoryday$(date +%s)"
}

gen_secret() {
    openssl rand -base64 64 2>/dev/null | tr -d '/+=' || echo "sk-$(date +%s | md5sum | cut -c1-32)"
}

# ============================================================
# 5. 部署服务
# ============================================================
deploy_services() {
    log_step "部署 MemoryDay 服务"

    # 选择部署模式
    echo ""
    echo "请选择部署模式:"
    echo "  1) IP+端口模式 (默认，快速测试使用)"
    echo "  2) 域名模式 (正式生产环境)"
    echo "  3) 仅生成配置文件 (手动部署)"
    echo ""
    read -p "请输入选项 [1-3] (默认 1): " DEPLOY_MODE
    DEPLOY_MODE=${DEPLOY_MODE:-1}

    DEPLOY_DIR=${DEPLOY_DIR:-/opt/memoryday}
    mkdir -p $DEPLOY_DIR

    # 获取项目源码
    SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPTS_DIR")"

    if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
        log_info "使用本地项目目录: $PROJECT_DIR"
        SOURCE_DIR="$PROJECT_DIR"
    else
        # 尝试从 Git 克隆
        if [ -z "$GIT_REPO" ]; then
            log_warn "未找到本地项目文件，请提供项目源码位置"
            echo ""
            echo "请选择源码来源:"
            echo "  1) 当前目录 (运行脚本的位置)"
            echo "  2) 指定 Git 仓库地址"
            echo "  3) 手动上传 (已在 $DEPLOY_DIR 中准备好)"
            echo ""
            read -p "请输入选项 [1-3] (默认 1): " SRC_OPTION
            SRC_OPTION=${SRC_OPTION:-1}

            case $SRC_OPTION in
                2)
                    read -p "请输入 Git 仓库地址: " GIT_REPO
                    if [ -n "$GIT_REPO" ]; then
                        log_info "克隆仓库: $GIT_REPO"
                        git clone "$GIT_REPO" /tmp/memoryday-src
                        SOURCE_DIR="/tmp/memoryday-src"
                    else
                        log_error "未提供仓库地址"
                        exit 1
                    fi
                    ;;
                3)
                    if [ -f "$DEPLOY_DIR/docker-compose.yml" ]; then
                        log_success "项目文件已就绪"
                        SOURCE_DIR="$DEPLOY_DIR"
                    else
                        log_error "未找到项目文件，请先上传到 $DEPLOY_DIR"
                        exit 1
                    fi
                    ;;
                *)
                    log_error "请将项目文件放到运行脚本的目录下"
                    exit 1
                    ;;
            esac
        else
            log_info "克隆仓库: $GIT_REPO"
            git clone "$GIT_REPO" /tmp/memoryday-src
            SOURCE_DIR="/tmp/memoryday-src"
        fi
    fi

    # 复制项目文件
    log_info "复制项目文件到 $DEPLOY_DIR ..."
    rsync -a --delete \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        "$SOURCE_DIR/" "$DEPLOY_DIR/" 2>/dev/null || \
    rsync -a --delete \
        --exclude='.git' \
        "$SOURCE_DIR/" "$DEPLOY_DIR/" 2>/dev/null

    # 创建必要目录
    mkdir -p $DEPLOY_DIR/backend/{logs,static,media}
    mkdir -p $DEPLOY_DIR/backend/docker/nginx/conf.d

    # 配置域名或 IP
    if [ "$DEPLOY_MODE" == "2" ]; then
        ACCESS_MODE="domain"
        while [ -z "$DOMAIN_NAME" ]; do
            read -p "请输入您的域名 (例如: memoryday.example.com): " DOMAIN_NAME
        done
        SERVER_NAME="$DOMAIN_NAME"
        log_info "域名模式: $DOMAIN_NAME"
    else
        ACCESS_MODE="ip"
        # 获取公网 IP
        SERVER_IP=$(curl -fsSL https://api.ipify.org 2>/dev/null || \
                    curl -fsSL https://ipinfo.io/ip 2>/dev/null || \
                    hostname -I | awk '{print $1}')
        SERVER_NAME="$SERVER_IP"
        log_info "IP 模式: $SERVER_IP"
    fi

    # 生成安全凭据
    DB_PASSWORD=$(gen_pass)
    DB_ROOT_PASSWORD=$(gen_pass)
    REDIS_PASSWORD=$(gen_pass)
    SECRET_KEY=$(gen_secret)

    # 保存凭据到安全文件
    CRED_FILE="$DEPLOY_DIR/.credentials"
    cat > $CRED_FILE << EOF
# ============================================
# MemoryDay 部署凭据 (请妥善保管!)
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')
# ============================================
DB_DATABASE=memoryday
DB_USER=memoryday_user
DB_PASSWORD=${DB_PASSWORD}
DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}
DJANGO_SECRET_KEY=${SECRET_KEY}
EOF
    chmod 600 $CRED_FILE

    # 生成 .env 文件
    log_info "生成环境配置..."
    cat > $DEPLOY_DIR/backend/.env << EOF
# Django Settings
DJANGO_SECRET_KEY=${SECRET_KEY}
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,${SERVER_NAME},*

# Database
MYSQL_DATABASE=memoryday
MYSQL_USER=memoryday_user
MYSQL_PASSWORD=${DB_PASSWORD}
MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
MYSQL_HOST=db
MYSQL_PORT=3306

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/2

# WeChat Mini Program
WECHAT_APPID=your-wechat-appid
WECHAT_SECRET=your-wechat-secret
WECHAT_TOKEN=your-wechat-token
WECHAT_AES_KEY=your-wechat-aes-key

# File Upload
MAX_FILE_SIZE=104857600
MAX_STORAGE_PER_USER=10737418240
UPLOAD_DIR=uploads

# Tencent Cloud COS
COS_ENABLED=False
COS_SECRET_ID=your-cos-secret-id
COS_SECRET_KEY=your-cos-secret-key
COS_BUCKET=memoryday-1259810697
COS_REGION=ap-beijing
COS_APP_ID=your-cos-app-id
COS_DOMAIN=your-cos-domain.com
COS_PREFIX=memoryday
COS_MAX_FILE_SIZE=5242880
COS_ALLOWED_TYPES=image/jpeg,image/png,image/gif,image/webp
COS_USE_SIGNED_URL=True
COS_DEFAULT_EXPIRES=3600

# CORS / Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost,http://127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/django.log

# Deployment
DEPLOYMENT_MODE=production
EOF
    log_success "环境配置已生成"

    # 生成 Nginx 配置
    log_info "生成 Nginx 配置..."
    cat > $DEPLOY_DIR/backend/docker/nginx/conf.d/memoryday.conf << NGINXEOF
upstream memoryday_backend {
    server backend:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name ${SERVER_NAME};
    client_max_body_size 100M;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # 静态文件 (1年缓存)
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 媒体文件 (7天缓存)
    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # API 代理
    location /api/ {
        proxy_pass http://memoryday_backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }

    # 健康检查
    location /health/ {
        proxy_pass http://memoryday_backend/api/health/;
    }

    # 根路径
    location / {
        return 301 /api/;
    }
}
NGINXEOF
    log_success "Nginx 配置已生成"

    # 生成 Docker Compose 配置
    log_info "生成 Docker Compose 配置..."
    cat > $DEPLOY_DIR/docker-compose.yml << DOCKERCOMPOSE
# MemoryDay 生产环境部署配置
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')

services:
  # 后端 API 服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: memoryday-backend
    restart: unless-stopped
    expose:
      - "8000"
    volumes:
      - ./backend/logs:/app/logs
      - ./backend/static:/app/static
      - ./backend/media:/app/media
      - ./backend/.env:/app/.env:ro
    environment:
      - DJANGO_SETTINGS_MODULE=memoryday_backend.settings.production
      - DEPLOYMENT_MODE=production
      - LOG_LEVEL=info
      - GUNICORN_WORKERS=4
      - MYSQL_HOST=db
      - REDIS_HOST=redis
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - memoryday-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 40s

  # MySQL 数据库
  db:
    image: mysql:8.0
    container_name: memoryday-db
    restart: unless-stopped
    expose:
      - "3306"
    environment:
      MYSQL_ROOT_PASSWORD: \${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: \${MYSQL_DATABASE}
      MYSQL_USER: \${MYSQL_USER}
      MYSQL_PASSWORD: \${MYSQL_PASSWORD}
    volumes:
      - db_data:/var/lib/mysql
      - ./backend/docker/mysql/init:/docker-entrypoint-initdb.d:ro
    networks:
      - memoryday-network
    command: |
      --default-authentication-plugin=mysql_native_password
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: memoryday-redis
    restart: unless-stopped
    expose:
      - "6379"
    command: redis-server --appendonly yes --requirepass \${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - memoryday-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Nginx 反向代理
  nginx:
    image: nginx:1.25-alpine
    container_name: memoryday-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./backend/docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./backend/docker/nginx/conf.d:/etc/nginx/conf.d:ro
      - ./backend/static:/app/static:ro
      - ./backend/media:/app/media:ro
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - memoryday-network

volumes:
  db_data:
    driver: local
  redis_data:
    driver: local

networks:
  memoryday-network:
    driver: bridge
DOCKERCOMPOSE
    log_success "Docker Compose 配置已生成"

    # 启动服务
    if [ "$DEPLOY_MODE" != "3" ]; then
        log_step "启动服务"

        cd $DEPLOY_DIR

        # 加载环境变量
        set -a
        source backend/.env
        set +a

        # 构建并启动
        log_info "构建 Docker 镜像..."
        $DOCKER_COMPOSE build --no-cache backend 2>&1 | tail -5

        log_info "启动所有服务..."
        $DOCKER_COMPOSE up -d

        # 等待服务启动
        log_info "等待服务就绪 (约 60 秒)..."
        local retry=0
        local max_retry=30
        while [ $retry -lt $max_retry ]; do
            if curl -sf http://localhost:8000/api/health/ >/dev/null 2>&1; then
                break
            fi
            sleep 2
            retry=$((retry + 1))
            echo -n "."
        done
        echo ""

        # 检查服务状态
        echo ""
        log_step "服务状态检查"

        $DOCKER_COMPOSE ps

        if curl -sf http://localhost:8000/api/health/ >/dev/null 2>&1; then
            log_success "后端 API 服务运行正常!"
        else
            log_warn "后端 API 可能尚未完全就绪，请稍后检查日志"
            log_info "日志查看: cd $DEPLOY_DIR && $DOCKER_COMPOSE logs -f backend"
        fi

        # 显示部署信息
        show_deploy_info
    else
        log_success "配置文件已生成，路径: $DEPLOY_DIR"
        log_info "手动启动: cd $DEPLOY_DIR && $DOCKER_COMPOSE up -d --build"
    fi
}

# ============================================================
# 6. 显示部署信息
# ============================================================
show_deploy_info() {
    echo ""
    echo "============================================"
    echo -e "  ${GREEN}MemoryDay 部署完成!${NC}"
    echo "============================================"
    echo ""
    echo "📊 服务访问地址:"
    echo "   - API 接口:    http://${SERVER_NAME}/api/"
    echo "   - API 文档:    http://${SERVER_NAME}/api/docs/"
    echo "   - 管理后台:    http://${SERVER_NAME}/api/admin/"
    echo "   - 健康检查:    http://${SERVER_NAME}/health/"
    echo ""
    echo "📁 部署目录:      $DEPLOY_DIR"
    echo "🔐 凭据文件:      $DEPLOY_DIR/.credentials (chmod 600)"
    echo ""
    echo "📝 常用命令:"
    echo "   查看日志:  cd $DEPLOY_DIR && $DOCKER_COMPOSE logs -f"
    echo "   停止服务:  cd $DEPLOY_DIR && $DOCKER_COMPOSE down"
    echo "   重启服务:  cd $DEPLOY_DIR && $DOCKER_COMPOSE restart"
    echo "   更新部署:  cd $DEPLOY_DIR && $DOCKER_COMPOSE up -d --build"
    echo "   查看状态:  cd $DEPLOY_DIR && $DOCKER_COMPOSE ps"
    echo ""
    echo "⚙️  小程序配置:"
    echo "   修改 miniprogram/app.js 中的配置:"
    echo "     accessMode: 'ip'  →  'ip' 或 'domain'"
    echo "     selfServer.ip.baseUrl: 'http://${SERVER_NAME}/api'"
    echo ""
    echo "⚠️  重要提示:"
    echo "   1. 请修改 backend/.env 中的微信小程序配置"
    echo "   2. 如需 HTTPS，请配置 SSL 证书"
    echo "   3. 凭据文件 .credentials 请妥善保管"
    echo "   4. 查看部署日志: $DOCKER_COMPOSE logs -f backend"
    echo ""
}

# ============================================================
# 7. 卸载
# ============================================================
uninstall() {
    log_step "卸载 MemoryDay 服务"
    log_warn "此操作将停止并删除所有容器和数据卷!"
    read -p "确认卸载? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "取消卸载"
        exit 0
    fi

    DEPLOY_DIR=${DEPLOY_DIR:-/opt/memoryday}
    if [ -f "$DEPLOY_DIR/docker-compose.yml" ]; then
        cd $DEPLOY_DIR
        $DOCKER_COMPOSE down -v
        log_success "容器已停止并删除"
    fi

    read -p "是否删除部署目录 $DEPLOY_DIR ? (yes/no): " confirm
    if [ "$confirm" == "yes" ]; then
        rm -rf $DEPLOY_DIR
        log_success "部署目录已删除"
    fi

    log_success "卸载完成"
}

# ============================================================
# 8. 更新部署
# ============================================================
update_deploy() {
    log_step "更新 MemoryDay 部署"

    DEPLOY_DIR=${DEPLOY_DIR:-/opt/memoryday}
    if [ ! -f "$DEPLOY_DIR/docker-compose.yml" ]; then
        log_error "未找到部署目录: $DEPLOY_DIR"
        log_info "请先执行部署 (./deploy.sh --deploy)"
        exit 1
    fi

    cd $DEPLOY_DIR

    # 如果是 Git 仓库，拉取最新代码
    if [ -d ".git" ]; then
        log_info "拉取最新代码..."
        git pull || log_warn "Git 拉取失败，使用现有代码"
    fi

    # 重新构建并启动
    log_info "重新构建镜像..."
    $DOCKER_COMPOSE build backend

    log_info "重启服务..."
    $DOCKER_COMPOSE up -d --force-recreate

    # 等待就绪
    sleep 10
    if curl -sf http://localhost:8000/api/health/ >/dev/null 2>&1; then
        log_success "更新成功!"
    else
        log_warn "服务可能未完全就绪，请检查日志"
    fi
}

# ============================================================
# 9. 显示帮助
# ============================================================
show_help() {
    echo "MemoryDay 通用一键部署脚本 v2.0"
    echo ""
    echo "用法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -d, --deploy      执行部署 (默认)"
    echo "  -u, --update      更新现有部署"
    echo "  -r, --remove      卸载并清理"
    echo "  -h, --help        显示帮助信息"
    echo ""
    echo "环境变量:"
    echo "  DEPLOY_DIR        部署目录 (默认: /opt/memoryday)"
    echo "  GIT_REPO          项目 Git 仓库地址"
    echo ""
    echo "示例:"
    echo "  # 交互式部署"
    echo "  curl -fsSL https://example.com/deploy.sh | bash"
    echo ""
    echo "  # 指定目录部署"
    echo "  DEPLOY_DIR=/data/memoryday ./deploy.sh"
    echo ""
    echo "  # 从 Git 仓库部署"
    echo "  GIT_REPO=https://github.com/user/memoryday.git ./deploy.sh"
    echo ""
    echo "  # 更新部署"
    echo "  ./deploy.sh --update"
    echo ""
    echo "  # 卸载"
    echo "  ./deploy.sh --remove"
    echo ""
}

# ============================================================
# 主入口
# ============================================================
main() {
    show_banner
    check_root

    # 检测 Docker Compose
    check_docker_compose

    local ACTION="deploy"

    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--deploy)   ACTION="deploy" ;;
            -u|--update)   ACTION="update" ;;
            -r|--remove)   ACTION="remove" ;;
            -h|--help)     show_help; exit 0 ;;
            *)             echo "未知选项: $1"; show_help; exit 1 ;;
        esac
        shift
    done

    case $ACTION in
        deploy)
            detect_os
            install_docker
            config_firewall
            deploy_services
            ;;
        update)
            update_deploy
            ;;
        remove)
            uninstall
            ;;
    esac
}

main "$@"