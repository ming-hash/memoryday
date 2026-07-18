# MemoryDay 部署总结文档

> **版本**: v2.0 | **更新日期**: 2026-07-18
> **适用场景**: 任意云服务器一键部署 (腾讯云、阿里云、华为云、AWS 等)

---

## 目录

1. [项目架构概述](#1-项目架构概述)
2. [部署前置检查清单](#2-部署前置检查清单)
3. [一键部署流程](#3-一键部署流程)
4. [部署后验证](#4-部署后验证)
5. [小程序端配置](#5-小程序端配置)
6. [日常运维指南](#6-日常运维指南)
7. [常见问题排查](#7-常见问题排查)
8. [安全最佳实践](#8-安全最佳实践)
9. [附录](#9-附录)

---

## 1. 项目架构概述

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    云服务器 (Linux)                        │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐   │
│  │  Nginx   │───▶│ Backend  │───▶│     MySQL 8.0    │   │
│  │  :80/443 │    │ Django   │    │   (数据持久化)    │   │
│  └──────────┘    │ Gunicorn │    └──────────────────┘   │
│       │          └──────────┘                            │
│       │               │         ┌──────────────────┐   │
│       │               └────────▶│     Redis 7      │   │
│       │                         │   (缓存/队列)     │   │
│       │                         └──────────────────┘   │
│       │                                                 │
│  ┌────┴────────────────────────────────────────────┐    │
│  │          微信小程序 (前端)                        │    │
│  │  通过 wx.request 调用 API                       │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 1.2 组件说明

| 组件 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| **Nginx** | nginx:1.25-alpine | 80/443 | 反向代理、静态文件服务、SSL 终止 |
| **Backend** | Django 4.2 + Gunicorn | 8000 | REST API 服务、业务逻辑 |
| **MySQL** | mysql:8.0 | 3306 | 主数据库（数据持久化） |
| **Redis** | redis:7-alpine | 6379 | 缓存、Session、Celery 队列 |
| **小程序** | 微信原生框架 | - | 前端 UI |

### 1.3 网络拓扑

```
微信小程序 ───▶ 公网 ───▶ 服务器:80 ───▶ Nginx ───▶ Backend:8000
                                                      │
                                              ┌───────┴───────┐
                                              ▼               ▼
                                           MySQL:3306     Redis:6379
```

---

## 2. 部署前置检查清单

### 2.1 服务器要求

| 配置项 | 最低要求 | 推荐配置 | 说明 |
|--------|---------|---------|------|
| **CPU** | 1核 | 2核+ | 影响 API 响应速度 |
| **内存** | 2GB | 4GB+ | MySQL + Redis 占用较多 |
| **磁盘** | 20GB | 50GB+ SSD | 图片存储需要空间 |
| **带宽** | 1Mbps | 5Mbps+ | 影响小程序加载速度 |
| **系统** | Linux Kernel 3.10+ | Ubuntu 22.04 / CentOS 7+ | 需支持 Docker |
| **端口** | 80, 443 开放 | - | 微信小程序仅支持 80/443 |

### 2.2 软件依赖（脚本自动安装）

- Docker Engine (24.0+)
- Docker Compose Plugin (v2.20+)
- curl、openssl、rsync

### 2.3 部署前准备

```bash
# 1. 确认服务器配置
uname -a
cat /proc/cpuinfo | grep processor | wc -l
free -h
df -h

# 2. 确认端口可用
ss -tlnp | grep -E '(:80|:443|:8000|:3306|:6379)'

# 3. 上传项目到服务器（或使用 Git 仓库）
scp -r /path/to/memoryday root@服务器IP:/opt/
# 或
git clone https://github.com/your-repo/memoryday.git /opt/memoryday
```

---

## 3. 一键部署流程

### 3.1 快速部署（推荐）

```bash
# 1. SSH 登录服务器
ssh root@你的服务器IP

# 2. 进入项目目录
cd /opt/memoryday

# 3. 运行一键部署脚本
cd scripts && chmod +x deploy.sh && ./deploy.sh

# 4. 根据提示选择部署模式
#    - 输入 1: IP+端口模式（快速测试）
#    - 输入 2: 域名模式（正式生产）
```

### 3.2 命令行参数部署

```bash
# 默认部署（交互式）
./deploy.sh

# 指定部署目录
DEPLOY_DIR=/data/memoryday ./deploy.sh

# 从 Git 仓库部署
GIT_REPO=https://github.com/user/memoryday.git ./deploy.sh

# 更新部署
./deploy.sh --update

# 卸载清理
./deploy.sh --remove
```

### 3.3 部署过程详解

部署脚本会自动执行以下步骤：

```
Step 1: 环境检测
    ├── 检查 root 权限
    ├── 检测操作系统 (Ubuntu/CentOS/Debian/OpenCloudOS...)
    └── 检测 Docker 安装状态

Step 2: 安装 Docker（如未安装）
    ├── 配置阿里云镜像加速
    ├── 安装 Docker Engine
    ├── 安装 Docker Compose Plugin
    └── 配置镜像加速器

Step 3: 配置防火墙
    ├── 开放端口 80, 443
    └── firewalld / ufw / iptables 自动适配

Step 4: 部署服务
    ├── 复制项目文件到部署目录
    ├── 生成安全随机密码 (32位)
    ├── 生成 .env 环境配置
    ├── 生成 Nginx 配置
    ├── 生成 Docker Compose 配置
    ├── 构建 Docker 镜像
    ├── 启动所有容器 (MySQL → Redis → Backend → Nginx)
    └── 健康检查

Step 5: 输出部署信息
    ├── API 访问地址
    ├── 凭据文件位置
    └── 小程序配置指引
```

### 3.4 部署目录结构

部署完成后，`/opt/memoryday` 目录结构如下：

```
/opt/memoryday/
├── docker-compose.yml          # 生产环境 Docker Compose 配置
├── backend/
│   ├── .env                    # 环境变量（含密码）
│   ├── Dockerfile              # 镜像构建
│   ├── docker/
│   │   ├── entrypoint.sh       # 容器入口脚本
│   │   ├── nginx/
│   │   │   ├── nginx.conf      # Nginx 主配置
│   │   │   └── conf.d/
│   │   │       └── memoryday.conf  # 站点配置
│   │   └── mysql/
│   │       └── init/           # 数据库初始化脚本
│   ├── logs/                   # 应用日志
│   ├── static/                 # 静态文件
│   └── media/                  # 上传文件
├── .credentials                # 凭据文件（chmod 600）
└── scripts/
    └── deploy.sh               # 部署脚本
```

---

## 4. 部署后验证

### 4.1 服务状态检查

```bash
# 进入部署目录
cd /opt/memoryday

# 查看所有容器状态
docker compose ps

# 输出示例：
# NAME                 STATUS                  PORTS
# memoryday-backend    Up 2 minutes (healthy)  8000/tcp
# memoryday-db         Up 2 minutes (healthy)  3306/tcp
# memoryday-nginx      Up 2 minutes            0.0.0.0:80->80/tcp
# memoryday-redis      Up 2 minutes (healthy)  6379/tcp
```

### 4.2 API 健康检查

```bash
# 基础健康检查
curl http://localhost/api/health/

# 详细 API 测试
curl http://localhost/api/health/
curl http://localhost/api/dishes/
curl http://localhost/api/users/

# 检查 API 文档
curl -s http://localhost/api/docs/ | head -20
```

### 4.3 数据库验证

```bash
# 检查数据库连接
docker exec -i memoryday-db mysql -u memoryday_user -p \
  -e "SHOW DATABASES; USE memoryday; SHOW TABLES;"

# 查看数据表
docker exec -i memoryday-db mysql -u memoryday_user -p \
  -e "USE memoryday; SELECT table_name FROM information_schema.tables WHERE table_schema='memoryday';"
```

### 4.4 Redis 验证

```bash
# 检查 Redis 连接
docker exec memoryday-redis redis-cli -a "$REDIS_PASSWORD" ping

# 检查 Redis 状态
docker exec memoryday-redis redis-cli -a "$REDIS_PASSWORD" info | grep -E "connected_clients|used_memory_human"
```

### 4.5 完整验证脚本

```bash
#!/bin/bash
# deploy-verify.sh - 部署验证脚本

echo "=== MemoryDay 部署验证 ==="
echo ""

# 1. 容器状态
echo "▶ 检查容器状态..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep memoryday

# 2. API 健康检查
echo ""
echo "▶ 检查 API 健康状态..."
HEALTH=$(curl -sf http://localhost/api/health/ && echo "OK" || echo "FAIL")
echo "  Health: $HEALTH"

# 3. 数据库
echo ""
echo "▶ 检查数据库..."
DB_OK=$(docker exec memoryday-db mysqladmin ping -h localhost --silent 2>/dev/null && echo "OK" || echo "FAIL")
echo "  MySQL: $DB_OK"

# 4. Redis
echo ""
echo "▶ 检查 Redis..."
REDIS_OK=$(docker exec memoryday-redis redis-cli ping 2>/dev/null && echo "OK" || echo "FAIL")
echo "  Redis: $REDIS_OK"

# 5. 服务端口
echo ""
echo "▶ 检查端口监听..."
ss -tlnp | grep -E ':80|:443' | head -5

echo ""
echo "=== 验证完成 ==="
```

---

## 5. 小程序端配置

### 5.1 修改 API 地址

编辑 `miniprogram/app.js`，配置服务器地址：

```javascript
// 访问模式配置
this.globalData = {
  // 可选: 'local' | 'ip' | 'domain' | 'cloudbase'
  accessMode: 'ip',

  // 自建服务器配置
  selfServer: {
    ip: {
      baseUrl: 'http://你的服务器IP/api',  // ← 修改这里
    },
    domain: {
      baseUrl: 'https://你的域名.com/api',  // ← 域名模式
    }
  },
}
```

### 5.2 微信小程序后台配置

在微信公众平台配置服务器域名：

| 域名类型 | 域名地址 |
|---------|---------|
| request 合法域名 | `http://你的服务器IP` 或 `https://你的域名.com` |
| uploadFile 合法域名 | 同上（如使用 COS 需添加 COS 域名） |
| downloadFile 合法域名 | 同上 |

### 5.3 配置模板

```javascript
// 场景示例:

// 场景1: 本地开发测试
accessMode: 'local'
// 小程序 → http://127.0.0.1:8000/api

// 场景2: 自建服务器 (IP)
accessMode: 'ip'
selfServer.ip.baseUrl: 'http://123.456.789.0/api'
// 小程序 → http://123.456.789.0/api

// 场景3: 自建服务器 (域名)
accessMode: 'domain'
selfServer.domain.baseUrl: 'https://memoryday.example.com/api'
// 小程序 → https://memoryday.example.com/api

// 场景4: CloudBase 云端
accessMode: 'cloudbase'
// 小程序 → 云函数
```

---

## 6. 日常运维指南

### 6.1 服务管理

```bash
# 进入部署目录
cd /opt/memoryday

# 查看所有服务状态
docker compose ps

# 查看实时日志
docker compose logs -f
docker compose logs -f backend      # 只看后端日志
docker compose logs -f nginx        # 只看 Nginx 日志

# 查看最后 100 行日志
docker compose logs --tail=100 backend

# 重启单个服务
docker compose restart backend

# 重启所有服务
docker compose restart

# 停止服务（不影响数据）
docker compose down

# 停止并删除数据卷（谨慎！）
docker compose down -v

# 重新构建并启动
docker compose up -d --build
```

### 6.2 数据备份

```bash
#!/bin/bash
# backup.sh - 数据库备份脚本

BACKUP_DIR="/opt/backups/memoryday"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份 MySQL
echo "备份 MySQL..."
docker exec memoryday-db mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" \
  --all-databases --single-transaction --quick \
  | gzip > $BACKUP_DIR/memoryday-mysql-$DATE.sql.gz

# 备份上传文件
echo "备份媒体文件..."
tar -czf $BACKUP_DIR/memoryday-media-$DATE.tar.gz \
  -C /opt/memoryday/backend media/

# 备份配置
echo "备份配置文件..."
cp /opt/memoryday/backend/.env $BACKUP_DIR/env-$DATE.bak

# 保留最近 30 天备份，删除旧备份
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.bak" -mtime +30 -delete

echo "备份完成: $BACKUP_DIR"
echo "  MySQL: memoryday-mysql-$DATE.sql.gz"
echo "  Media: memoryday-media-$DATE.tar.gz"
```

### 6.3 数据恢复

```bash
# 恢复 MySQL
zcat /opt/backups/memoryday/memoryday-mysql-20260101_120000.sql.gz | \
  docker exec -i memoryday-db mysql -u root -p"$MYSQL_ROOT_PASSWORD"

# 恢复媒体文件
tar -xzf /opt/backups/memoryday/memoryday-media-20260101_120000.tar.gz \
  -C /opt/memoryday/backend/
```

### 6.4 服务更新

```bash
# 方式1：使用部署脚本更新
cd /opt/memoryday/scripts
./deploy.sh --update

# 方式2：手动更新
cd /opt/memoryday

# 拉取最新代码（如果是 Git 仓库）
git pull

# 重新构建并启动
docker compose up -d --build

# 查看更新日志
docker compose logs -f backend --tail=50
```

### 6.5 监控告警

```bash
# 检查后端资源使用
docker stats memoryday-backend memoryday-db memoryday-redis memoryday-nginx --no-stream

# 磁盘使用
df -h /opt/memoryday

# 日志轮转（Docker 已配置 10MB 上限）
# 查看日志大小
ls -lh /opt/memoryday/backend/logs/

# 查看容器日志大小
docker inspect memoryday-backend | grep LogPath | xargs ls -lh
```

---

## 7. 常见问题排查

### 7.1 部署失败

| 问题 | 原因 | 解决 |
|------|------|------|
| `Docker 安装失败` | 系统不兼容或网络问题 | 手动安装 Docker 后重新运行脚本 |
| `端口被占用` | 已有服务占用 80/443 | `ss -tlnp \| grep :80` 查看并停用冲突服务 |
| `镜像拉取超时` | 网络原因 | 已配置镜像加速器，若仍失败可手动 `docker pull` |
| `数据库连接失败` | MySQL 未就绪 | 等待 30 秒后重试，检查 `docker logs memoryday-db` |
| `API 返回 502` | 后端未就绪 | 等待后端启动完成，检查 `docker logs memoryday-backend` |

### 7.2 运行时问题

```bash
# 问题：API 响应慢
# 排查方法：
# 1. 检查数据库连接数
docker exec memoryday-db mysqladmin status

# 2. 检查 Redis 缓存命中率
docker exec memoryday-redis redis-cli info stats | grep hits

# 3. 检查 CPU/内存
docker stats --no-stream

# 问题：文件上传失败
# 排查方法：
# 1. 检查磁盘空间
df -h

# 2. 检查 Nginx 上传大小限制
grep client_max_body_size /opt/memoryday/backend/docker/nginx/conf.d/*.conf

# 3. 检查 COS 配置（如果启用）
docker exec memoryday-backend python manage.py cos_status
```

### 7.3 小程序无法连接

```bash
# 1. 服务器端排查
# 检查 Nginx 是否正常监听
ss -tlnp | grep ':80'

# 检查 API 是否可访问
curl -v http://localhost/api/health/

# 2. 小程序端排查
# 检查配置
#   - accessMode 是否正确
#   - baseUrl 是否指向正确的服务器 IP/域名
# 3. 微信后台排查
#   - request 合法域名是否已配置
#   - 服务器 IP 是否在白名单（如适用）
```

---

## 8. 安全最佳实践

### 8.1 部署后立即执行

```bash
# 1. 修改默认密码
# 编辑 /opt/memoryday/backend/.env
# 修改 WECHAT_SECRET 为真实值
# 配置 COS 密钥（如使用）

# 2. 限制 .credentials 文件权限
chmod 600 /opt/memoryday/.credentials

# 3. 配置 HTTPS（推荐使用 Let's Encrypt）
docker compose exec nginx apk add certbot
certbot --nginx -d your-domain.com

# 4. 配置数据库白名单
# 编辑 /opt/memoryday/docker-compose.yml
# 为 MySQL 添加 IP 限制
```

### 8.2 安全加固清单

- [ ] 修改所有默认密码（数据库、Redis、Django）
- [ ] 配置 HTTPS 证书
- [ ] 设置服务器防火墙（仅开放 80/443）
- [ ] 启用 fail2ban 防止暴力破解
- [ ] 定期更新 Docker 镜像
- [ ] 配置日志轮转
- [ ] 设置定期备份
- [ ] 监控服务器资源使用
- [ ] 限制 SSH 登录方式（密钥登录）
- [ ] 配置 Docker 安全策略

### 8.3 HTTPS 配置（Let's Encrypt）

```bash
# 安装 certbot
docker compose exec nginx apk add certbot certbot-nginx

# 申请证书
docker compose exec nginx certbot --nginx \
  -d your-domain.com \
  --non-interactive \
  --agree-tos \
  --email admin@your-domain.com

# 配置自动续期
echo "0 3 * * * docker exec memoryday-nginx certbot renew --quiet" | crontab -

# 更新 Nginx 配置（添加 HTTPS 监听）
# 编辑 /opt/memoryday/backend/docker/nginx/conf.d/memoryday.conf
# 添加 SSL 相关配置
```

---

## 9. 附录

### 9.1 文件索引

| 文件 | 路径 | 说明 |
|------|------|------|
| 部署脚本 | `scripts/deploy.sh` | 一键部署脚本 |
| 入口脚本 | `backend/docker/entrypoint.sh` | 容器启动入口 |
| 环境配置 | `backend/.env` | 所有环境变量 |
| 凭据文件 | `.credentials` | 自动生成的密码 |
| 部署配置 | `docker-compose.yml` | 生产环境 Docker Compose |
| Nginx 配置 | `backend/docker/nginx/conf.d/memoryday.conf` | 反向代理配置 |
| 小程序配置 | `miniprogram/app.js` | 小程序 API 地址配置 |

### 9.2 快速参考命令

```bash
# ===== 部署相关 =====
cd /opt/memoryday/scripts && ./deploy.sh          # 一键部署
./deploy.sh --update                                # 更新部署
./deploy.sh --remove                                # 卸载

# ===== 服务管理 =====
docker compose ps                                   # 查看状态
docker compose logs -f backend                      # 查看日志
docker compose restart backend                      # 重启服务
docker compose up -d --build                        # 重新构建

# ===== 数据库 =====
docker exec -it memoryday-db mysql -u root -p       # 进入 MySQL
docker exec -it memoryday-redis redis-cli           # 进入 Redis

# ===== 备份恢复 =====
bash /opt/memoryday/scripts/backup.sh               # 运行备份
```

### 9.3 部署验证清单

部署完成后，请逐项确认：

- [ ] 容器全部正常运行 (`docker compose ps` 全部为 `Up`)
- [ ] API 健康检查通过 (`curl http://localhost/api/health/`)
- [ ] 数据库连接正常
- [ ] Redis 缓存服务正常
- [ ] 小程序可以正常访问 API
- [ ] 静态文件正常加载
- [ ] 文件上传功能正常
- [ ] 微信小程序后台域名已配置
- [ ] 凭据文件已妥善保管
- [ ] HTTPS 已配置（正式环境）

### 9.4 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v2.0 | 2026-07-18 | 重写部署脚本，支持多系统、多模式、自动备份、健康检查 |
| v1.0 | 2026-01-24 | 初始部署方案 |

---

> **文档维护**: 如有问题或建议，请提交 Issue 或 Pull Request
> **最后更新**: 2026-07-18