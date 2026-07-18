# MemoryDay 部署上下文 (2026-07-18)

## 服务器信息

| 项目 | 值 |
|------|-----|
| **服务器 IP** | `1.14.61.155` |
| **SSH 用户** | `root` |
| **SSH 密码** | `uos@12345` |
| **系统** | OpenCloudOS 9.6 |
| **项目远程路径** | `/opt/memoryday/` |
| **本地项目路径** | `/home/ming/Desktop/统信/小程序/memoryday/` |

## 当前容器状态（全部运行中）

| 容器 | 状态 | 端口 |
|------|------|------|
| `memoryday-backend` | ✅ **健康** (Up 24 min) | 8000 (内部) |
| `memoryday-db` | ✅ **健康** | 3306 (内部) |
| `memoryday-redis` | ✅ **健康** | 6379 (内部) |
| `memoryday-nginx` | ✅ **运行中** | 80, 443 (外部) |

## 凭据

```bash
DB_PASSWORD=vdEWaI6fl8kw3dfKicEZ6FTP
DB_ROOT_PASSWORD=vdEWaI6fl8kw3dfKicEZ6FTProot
REDIS_PASSWORD=BTvvqjC61V5fVtRkRmW8niO3
DJANGO_SECRET_KEY=SppTWNPI5DpjJzsewExR7IUmkXBDIpXwSkqBT2G4Qlgf5FTsP1KLVniHqkqnXnd9E3I5pu91KVodYIXRDxQ
```

- 本地凭据文件：`/home/ming/Desktop/统信/小程序/memoryday/.credentials`
- 远程 .env 文件：`/opt/memoryday/backend/.env`

## 已修改的文件（需同步到远程）

1. **`backend/Dockerfile`** — 添加了腾讯云镜像源（APT + pip）
2. **`backend/requirements.txt`** — 添加了 `requests==2.31.0` 和 `cos-python-sdk-v5==1.9.24`
3. **`backend/docker/nginx/conf.d/memoryday.conf`** — 将 `server web:8000` 改为 `server backend:8000`
4. **`docker-compose.prod.yml`** — 新文件，生产环境专用配置（禁用 SSL 重定向）

## 待解决问题

### 问题 1：环境变量未加载

启动时必须使用 `--env-file` 参数，否则 MySQL/Redis 密码为空：

```bash
# ✅ 正确方式
cd /opt/memoryday
docker compose --env-file backend/.env up -d

# ❌ 错误方式（密码不生效）
docker compose up -d
```

### 问题 2：后端返回 301 重定向（SSL 重定向）

`/api/health/` 返回 301，需要在 production.py 中关闭 SECURE_SSL_REDIRECT。

> 虽然在 `docker-compose.prod.yml` 中设置了 `SECURE_SSL_REDIRECT=False`，但需要确认 production.py 没有硬编码为 True。

### 问题 3：docker-compose.prod.yml 未使用

当前远程服务器使用的是 `docker-compose.yml`（含 SSL 重定向），未启用 `docker-compose.prod.yml`。

## 推荐修复命令

SSH 登录后依次执行：

```bash
# 1. 同步本地修改到远程
# 在本地执行：
# rsync -avz --include="Dockerfile" --include="requirements.txt" --exclude="*" \
#   -e "ssh -o StrictHostKeyChecking=no" \
#   backend/ root@1.14.61.155:/opt/memoryday/backend/

# 2. 停止服务
cd /opt/memoryday
docker compose --env-file backend/.env down

# 3. 重新构建（含新依赖）
docker compose --env-file backend/.env build --no-cache backend

# 4. 启动所有服务
docker compose --env-file backend/.env up -d --force-recreate

# 5. 验证
docker compose ps
curl -s http://localhost:8000/api/health/
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost/api/health/
echo ""

# 或使用 docker-compose.prod.yml（已禁用 SSL）
docker compose -f docker-compose.prod.yml --env-file backend/.env up -d --force-recreate
```

## 后续可做

- [ ] **配置 HTTPS**: 使用 Certbot 申请 Let's Encrypt 证书
- [ ] **小程序对接**: 在微信开发者工具中配置 API 地址 `http://1.14.61.155/api/`
- [ ] **部署云函数**: `cloudfunctions/` 目录中的微信云函数
- [ ] **配置 WebSocket**: 如有实时功能需要
