#!/bin/bash
# ============================================
# MemoryDay 生产环境容器入口脚本
# ============================================
set -e

echo "============================================"
echo "  MemoryDay 后端服务启动"
echo "============================================"

# 等待数据库就绪
echo "[1/5] 等待数据库就绪..."
if [ -n "$MYSQL_HOST" ]; then
    until mysqladmin ping -h"$MYSQL_HOST" -P"${MYSQL_PORT:-3306}" --silent 2>/dev/null; do
        echo "  等待数据库连接..."
        sleep 2
    done
    echo "  ✓ 数据库连接成功"
fi

# 执行数据库迁移
echo "[2/5] 执行数据库迁移..."
python manage.py migrate --noinput
echo "  ✓ 数据库迁移完成"

# 收集静态文件
echo "[3/5] 收集静态文件..."
python manage.py collectstatic --noinput --clear 2>/dev/null || python manage.py collectstatic --noinput
echo "  ✓ 静态文件收集完成"

# 创建超级管理员（如果环境变量有配置）
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "[4/5] 创建超级管理员..."
    python manage.py createsuperuser \
        --noinput \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "${DJANGO_SUPERUSER_EMAIL:-admin@memoryday.com}" 2>/dev/null || true
    echo "  ✓ 超级管理员已就绪"
else
    echo "[4/5] 跳过超级管理员创建（未配置环境变量）"
fi

# 启动 Gunicorn 服务
echo "[5/5] 启动 Gunicorn 服务..."
echo "  监听地址: 0.0.0.0:8000"
echo "  Worker 数: ${GUNICORN_WORKERS:-4}"
echo "============================================"

exec gunicorn memoryday_backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --worker-class sync \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info}