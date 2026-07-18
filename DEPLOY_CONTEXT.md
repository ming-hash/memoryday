# MemoryDay 部署上下文 (示例模板)

> ⚠️ **安全提醒**: 本文件包含占位符信息，实际部署时请替换为真实值。
> 请勿将真实凭据提交到 Git 仓库。

## 服务器信息

| 项目 | 值（示例） |
|------|-----------|
| **服务器 IP** | `your-server-ip` |
| **SSH 用户** | `root` |
| **SSH 密码** | `your-ssh-password` |
| **系统** | OpenCloudOS 9.6 |
| **项目远程路径** | `/opt/memoryday/` |
| **本地项目路径** | `/path/to/memoryday/` |

## 容器状态

| 容器 | 状态 | 端口 |
|------|------|------|
| `memoryday-backend` | 运行中 | 8000 (内部) |
| `memoryday-db` | 运行中 | 3306 (内部) |
| `memoryday-redis` | 运行中 | 6379 (内部) |
| `memoryday-nginx` | 运行中 | 80, 443 (外部) |

## 凭据（示例）

```bash
DB_PASSWORD=your-db-password
DB_ROOT_PASSWORD=your-db-root-password
REDIS_PASSWORD=your-redis-password
DJANGO_SECRET_KEY=your-django-secret-key
```

- 本地凭据文件：`/path/to/memoryday/.credentials`
- 远程 .env 文件：`/opt/memoryday/backend/.env`

## 已修改的文件（需同步到远程）

1. **`backend/Dockerfile`** — 添加了腾讯云镜像源（APT + pip）
2. **`backend/requirements.txt`** — 添加了 `requests==2.31.0` 和 `cos-python-sdk-v5==1.9.24`
3. **`backend/docker/nginx/conf.d/memoryday.conf`** — 将 `server web:8000` 改为 `server backend:8000`
4. **`docker-compose.prod.yml`** — 生产环境专用配置

## 推荐修复命令

SSH 登录后依次执行：

```bash
# 1. 同步本地修改到远程
# 在本地执行：
# rsync -avz --include="Dockerfile" --include="requirements.txt" --exclude="*" \
#   -e "ssh -o StrictHostKeyChecking=no" \
#   backend/ root@your-server-ip:/opt/memoryday/backend/

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
```

## 后续可做

- [ ] **配置 HTTPS**: 使用 Certbot 申请 Let's Encrypt 证书
- [ ] **小程序对接**: 在微信开发者工具中配置 API 地址
- [ ] **部署云函数**: `cloudfunctions/` 目录中的微信云函数
- [ ] **配置 WebSocket**: 如有实时功能需要