# MemoryDay Project Memory

## 项目概况
- MemoryDay：微信小程序 + Django 后端（统信 UOS 项目）
- 本地路径：`/home/ming/Desktop/统信/小程序/memoryday/`
- 远程服务器：1.14.61.155 (OpenCloudOS 9.6)
- SSH 登录：root / uos@12345
- 项目目录：`/opt/memoryday/`

## 部署状态 (2026-07-18)
### 已完成
- Docker 及 Docker Compose 已安装（通过腾讯云镜像源）
- 项目文件已上传至 `/opt/memoryday/`
- 4 个容器已成功构建并运行，均使用 `docker-compose.prod.yml` + `--env-file backend/.env`
  - `memoryday-backend` - ✅ 健康 (8000/tcp)
  - `memoryday-db` - ✅ 健康 (3306/tcp)
  - `memoryday-redis` - ✅ 健康 (6379/tcp)
  - `memoryday-nginx` - ✅ 运行中 (80/443)
- Nginx 监听 80/443 端口
- 国内镜像已配置（Dockerfile 使用腾讯云镜像）
- 依赖已添加：`requests==2.31.0`, `cos-python-sdk-v5==1.9.24`
- **健康检查端点**：`/api/health/` 返回 `{"status":"healthy",...}`（已修复 404 问题）
- **SSL 重定向已关闭**：`production.py` 中 `SECURE_SSL_REDIRECT` 改为从环境变量读取，默认 False
- **环境变量已正确加载**：使用 `--env-file backend/.env` 参数启动

### 待完成
- [ ] **配置 HTTPS**: 使用 Certbot 申请 Let's Encrypt 证书
- [ ] **小程序对接**: 在微信开发者工具中配置 API 地址 `http://1.14.61.155/api/`
- [ ] **部署云函数**: `cloudfunctions/` 目录中的微信云函数
- [ ] **配置 WebSocket**: 如有实时功能需要

### 关键修复点
1. `production.py` line 9: `SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)`（原为硬编码 True）
2. `urls.py` line 42: 添加了 `path('api/health/', health_check, name='health-check')` 健康检查端点
3. `docker-compose.prod.yml`：使用 `--env-file backend/.env` 加载环境变量，各环境变量均通过 `${VAR}` 引用

### 管理命令
```bash
# 启动（生产环境）
cd /opt/memoryday
docker compose -f docker-compose.prod.yml --env-file backend/.env up -d

# 停止
docker compose -f docker-compose.prod.yml --env-file backend/.env down

# 重建并启动
docker compose -f docker-compose.prod.yml --env-file backend/.env up -d --build

# 查看日志
docker compose -f docker-compose.prod.yml --env-file backend/.env logs --tail=50 backend
```

### 凭据
- 文件：`/home/ming/Desktop/统信/小程序/memoryday/.credentials`
- DB_PASSWORD=vdEWaI6fl8kw3dfKicEZ6FTP
- REDIS_PASSWORD=BTvvqjC61V5fVtRkRmW8niO3
- DJANGO_SECRET_KEY=SppTWNPI5DpjJzsewExR7IUmkXBDIpXwSkqBT2G4Qlgf5FTsP1KLVniHqkqnXnd9E3I5pu91KVodYIXRDxQ