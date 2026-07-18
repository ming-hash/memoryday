#!/bin/bash
# ============================================================
# MemoryDay 部署验证脚本
# 部署完成后运行，验证所有服务是否正常
# ============================================================

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

PASS=0
FAIL=0
DEPLOY_DIR=${DEPLOY_DIR:-/opt/memoryday}

check() {
    local desc="$1"
    local cmd="$2"
    echo -n "  [ ] $desc ... "
    if eval "$cmd" &>/dev/null; then
        echo -e "${GREEN}通过${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}失败${NC}"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     MemoryDay 部署验证报告              ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}━━━ 1. 容器状态 ━━━${NC}"
check "Docker 运行中"         "docker info"
check "Backend 容器运行中"    "docker ps --filter name=memoryday-backend --filter status=running --format '{{.Names}}' | grep -q memoryday-backend"
check "MySQL 容器运行中"      "docker ps --filter name=memoryday-db --filter status=running --format '{{.Names}}' | grep -q memoryday-db"
check "Redis 容器运行中"      "docker ps --filter name=memoryday-redis --filter status=running --format '{{.Names}}' | grep -q memoryday-redis"
check "Nginx 容器运行中"      "docker ps --filter name=memoryday-nginx --filter status=running --format '{{.Names}}' | grep -q memoryday-nginx"

echo ""
echo -e "${BLUE}━━━ 2. 健康检查 ━━━${NC}"
check "Backend 健康检查"      "curl -sf http://localhost:8000/api/health/"
check "Nginx 代理 API"        "curl -sf http://localhost/api/health/"

echo ""
echo -e "${BLUE}━━━ 3. 端口监听 ━━━${NC}"
check "端口 80 已监听"        "ss -tlnp | grep -q ':80 '"
check "端口 443 已监听"       "ss -tlnp | grep -q ':443 '"

echo ""
echo -e "${BLUE}━━━ 4. 数据库 ━━━${NC}"
check "MySQL 连接正常"        "docker exec memoryday-db mysqladmin ping -h localhost --silent"
check "MySQL 数据库存在"      "docker exec memoryday-db mysql -u memoryday_user -p\$MYSQL_PASSWORD memoryday -e 'SELECT 1' 2>/dev/null"

echo ""
echo -e "${BLUE}━━━ 5. Redis ━━━${NC}"
check "Redis 连接正常"        "docker exec memoryday-redis redis-cli ping 2>/dev/null | grep -q PONG"

echo ""
echo -e "${BLUE}━━━ 6. 文件系统 ━━━${NC}"
check "部署目录存在"          "test -d $DEPLOY_DIR"
check "配置目录存在"          "test -d $DEPLOY_DIR/backend"
check "日志目录存在"          "test -d $DEPLOY_DIR/backend/logs"
check "静态文件目录存在"      "test -d $DEPLOY_DIR/backend/static"
check "环境配置文件存在"      "test -f $DEPLOY_DIR/backend/.env"
check "Docker Compose 存在"   "test -f $DEPLOY_DIR/docker-compose.yml"

echo ""
echo -e "${BLUE}━━━ 7. 网络连通性 ━━━${NC}"
check "Nginx → Backend 连通"  "docker exec memoryday-nginx curl -sf http://memoryday-backend:8000/api/health/ 2>/dev/null || docker exec memoryday-nginx curl -sf http://backend:8000/api/health/ 2>/dev/null"

echo ""
echo "════════════════════════════════════════"
echo -e "  验证结果: ${GREEN}$PASS 通过${NC} | ${RED}$FAIL 失败${NC} | $((PASS + FAIL)) 总计"
echo "════════════════════════════════════════"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}所有检查通过！部署成功 🎉${NC}"
else
    echo -e "${RED}存在 $FAIL 项检查失败，请排查问题${NC}"
    echo "查看日志: docker compose -f $DEPLOY_DIR/docker-compose.yml logs -f"
fi
echo ""