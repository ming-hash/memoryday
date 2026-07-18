#!/bin/bash
# ============================================================
# MemoryDay 数据库备份脚本
# 可添加到 crontab 定时执行
# ============================================================

set -e

BACKUP_DIR=${BACKUP_DIR:-/opt/backups/memoryday}
DEPLOY_DIR=${DEPLOY_DIR:-/opt/memoryday}
RETENTION_DAYS=${RETENTION_DAYS:-30}
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cd $DEPLOY_DIR

# 从 .env 加载密码
source backend/.env 2>/dev/null || true

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始备份..."

# 1. 备份 MySQL
echo "  备份 MySQL 数据库..."
docker exec memoryday-db mysqldump \
    -u root -p"$MYSQL_ROOT_PASSWORD" \
    --all-databases \
    --single-transaction \
    --quick \
    --routines \
    --triggers \
    --events 2>/dev/null | gzip > "$BACKUP_DIR/memoryday-mysql-$DATE.sql.gz"

# 2. 备份媒体文件
echo "  备份媒体文件..."
tar -czf "$BACKUP_DIR/memoryday-media-$DATE.tar.gz" \
    -C "$DEPLOY_DIR/backend" media/ 2>/dev/null || true

# 3. 备份配置文件
echo "  备份配置文件..."
cp "$DEPLOY_DIR/backend/.env" "$BACKUP_DIR/env-$DATE.bak"
cp "$DEPLOY_DIR/.credentials" "$BACKUP_DIR/credentials-$DATE.bak" 2>/dev/null || true

# 4. 清理过期备份
echo "  清理 $RETENTION_DAYS 天前的备份..."
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.bak" -mtime +$RETENTION_DAYS -delete

# 5. 统计
MYSQL_SIZE=$(ls -lh "$BACKUP_DIR/memoryday-mysql-$DATE.sql.gz" | awk '{print $5}')
MEDIA_SIZE=$(ls -lh "$BACKUP_DIR/memoryday-media-$DATE.tar.gz" | awk '{print $5}')
TOTAL_SIZE=$(du -sh $BACKUP_DIR | awk '{print $1}')

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 备份完成!"
echo "  MySQL 备份: $BACKUP_DIR/memoryday-mysql-$DATE.sql.gz ($MYSQL_SIZE)"
echo "  媒体备份:   $BACKUP_DIR/memoryday-media-$DATE.tar.gz ($MEDIA_SIZE)"
echo "  备份总大小: $TOTAL_SIZE"