# MemoryDay Project Memory

## 项目概况
- MemoryDay：微信小程序 + Django 后端（统信 UOS 项目）
- 本地路径：`/home/ming/Desktop/统信/小程序/memoryday/`
- 远程服务器：1.14.61.155 (OpenCloudOS 9.6)
- SSH 登录：root / uos@12345（通过密钥）
- 项目目录：`/opt/memoryday/`

## 部署状态 (2026-07-18 第2轮修复后)
### 已完成
- ✅ Docker 及 Docker Compose 已安装（通过腾讯云镜像源）
- ✅ 项目文件已上传至 `/opt/memoryday/`
- ✅ 4 个容器已成功构建并运行，均使用 `docker-compose.prod.yml` + `--env-file backend/.env`
- ✅ Nginx 监听 80/443 端口
- ✅ 国内镜像已配置（Dockerfile 使用腾讯云镜像）
- ✅ 健康检查端点 `/api/health/` 正常工作
- ✅ SSL 重定向已关闭（`production.py` 中 `SECURE_SSL_REDIRECT` 默认 False）
- ✅ 环境变量已正确加载
- ✅ **Redis 缓存修复**：改用 `django_redis.cache.RedisCache`，缓存功能正常
- ✅ **SMS 验证码登录修复**：Serializer 不再拦截认证，View 统一处理密码+SMS码
- ✅ **Token 存储修复**：所有文件改用 `StorageService.getToken()` 解包 token
- ✅ **文件上传**：POST `/api/upload/upload/` 正常工作，文件持久化到宿主机的 `/opt/memoryday/backend/media/uploads/`
- ✅ **media 目录持久化**：docker-compose.prod.yml 中 `./backend/media:/app/media` 已配置

### 待完成
- [ ] **配置 HTTPS**: 使用 Certbot 申请 Let's Encrypt 证书（Nginx 443 端口已开）
- [ ] **小程序对接**: 在微信开发者工具中配置 API 地址 `http://1.14.61.155/api/`
- [ ] **部署云函数**: `cloudfunctions/` 目录中的微信云函数
- [ ] **配置 WebSocket**: 如有实时功能需要

### 关键修复点
1. `production.py`: `SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)`
2. `urls.py`: 添加了 `path('api/health/', health_check)` 健康检查端点
3. `settings.py` / `settings/production.py`: 缓存 BACKEND 从 `django.core.cache.backends.redis.RedisCache` 改为 `django_redis.cache.RedisCache`
4. `backend/apps/users/serializers.py`: 移除 `UserLoginSerializer.validate()` 中的 `authenticate()` 调用，改为纯字段校验
5. `backend/apps/users/views.py`: `login_user()` 统一处理密码哈希校验 + SMS 验证码缓存校验
6. `services/cosService.js`: 导入 StorageService，`uploadImageToLocal()` 用 `StorageService.getToken()`
7. `utils/api.js` / `utils/wxcloud-api.js`: 所有 `wx.getStorageSync('token')` 改为 `StorageService.getToken()`

### 管理命令
```bash
# 启动/停止/重建
cd /opt/memoryday
docker compose -f docker-compose.prod.yml --env-file backend/.env up -d
docker compose -f docker-compose.prod.yml --env-file backend/.env down
docker compose -f docker-compose.prod.yml --env-file backend/.env up -d --build

# 查看日志
docker compose -f docker-compose.prod.yml --env-file backend/.env logs --tail=50 backend

# 同步文件到容器
docker cp /opt/memoryday/backend/apps/users/views.py memoryday-backend:/app/apps/users/views.py
docker restart memoryday-backend
```

### 测试用户（服务器数据库内）
- 手机号: `13800138000`，密码: `test123456`，昵称: 测试用户
- 登录支持 SMS 验证码（先 POST `/api/auth/send-sms-code/` 获取码）

### 凭据
- 文件：`.credentials`（项目根目录）
- DB_PASSWORD=vdEWaI6fl8kw3dfKicEZ6FTP
- REDIS_PASSWORD=BTvvqjC61V5fVtRkRmW8niO3
- DJANGO_SECRET_KEY=SppTWNPI5DpjJzsewExR7IUmkXBDIpXwSkqBT2G4Qlgf5FTsP1KLVniHqkqnXnd9E3I5pu91KVodYIXRDxQ