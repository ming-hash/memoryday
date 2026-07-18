# MemoryDay 图片上传问题排查总结 (2026-07-18)

## 问题现象
用户反馈：上传图片失败。后端日志中完全没有来自小程序的任何请求（只有健康检查的 curl 测试记录）。

## 排查过程

### 步骤 1: 检查服务器日志
```bash
ssh root@your-server-ip
docker logs memoryday-backend --tail 100
docker logs memoryday-nginx --tail 50
```

**发现**: 后端日志只有健康检查记录，**没有来自小程序的任何 API 请求**。

### 步骤 2: 检查小程序 API 配置
检查了 `app.js` 中的 `app.request` 方法、`services/cosService.js`、`utils/deployment.js` 等。

**发现一**: 小程序项目根目录（`/home/ming/Desktop/统信/小程序/memoryday/`）下有**两个 app.js**：
- **根目录 `app.js`** — 微信小程序的入口文件（正确）
- **`miniprogram/app.js`** — 可能存在冲突

**发现二**: 小程序使用 `app.request()` 封装的请求方法，所有 API 都需要 JWT token 认证。

### 步骤 3: 检查用户认证状态
```bash
# 使用自定义 User 模型（在 apps.users.models 中）
docker exec memoryday-backend python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memoryday_backend.settings.production')
import django; django.setup()
from apps.users.models import User
users = User.objects.all()
print(f'用户数: {users.count()}')
"
```

**发现三**: **数据库中没有任何用户！** 上传接口 `@permission_classes([permissions.IsAuthenticated])` 需要登录认证，所有未认证请求返回 401，小程序端没有正确处理 401 导致上传失败。

### 步骤 4: 创建测试用户
```bash
docker exec -i memoryday-backend python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memoryday_backend.settings.production')
import django; django.setup()
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

user = User.objects.create_user(
    phone='your-test-phone',
    password='your-test-password',
    nickname='测试用户',
    is_active=True
)
refresh = RefreshToken.for_user(user)
print('Access Token:', str(refresh.access_token))
"
```
- 登录接口字段: `username`（实际传手机号）+ `password`
- Token 已创建

### 步骤 5: 测试上传 API
```bash
# 先登录获取 token
curl -s -X POST http://localhost/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"your-test-phone","password":"your-test-password"}'
```

**发现四**: 上传接口返回 **500 错误**，`UploadedFile` 模型字段名与视图代码不匹配。视图使用了 `file_path`、`content_type` 等字段，但模型中实际字段名为 `storage_path`、`mime_type` 等。

**发现五**: 上传目录 `/app/media/uploads/` 在容器中不存在或权限不足。

**发现六**: Nginx 容器通过宿主机 `/opt/memoryday/backend/media/` 目录提供媒体文件访问，但 Django 容器未挂载该目录，文件仅保存在容器内部。

### 步骤 6: 登录/注册流程问题
检查 `pages/login/login.js`：
- 小程序使用 `username`（手机号）+ `password` 登录
- 调用 `POST /api/auth/login/`
- 登录成功后保存 token 到 `wx.setStorageSync('token', ...)`
- 后续请求在 `app.request()` 中通过 `Authorization: Bearer <token>` 携带

## 已修复的问题

### 修复 1: 上传目录权限
```bash
docker exec -u root memoryday-backend chown -R django:django /app/media
docker exec memoryday-backend mkdir -p /app/media/uploads
```

### 修复 2: `backend/apps/upload/views.py` 字段名不匹配
将视图中的 `file_path`、`content_type`、`created_at` 等改为 `UploadedFile` 模型实际字段名：
- `file_path` → `storage_path`
- `content_type` → `mime_type`（加上 `file_type` 分类）
- `created_at` → 保留，但模型实际使用的字段需要确认
- 删除了 `file_extension`、`storage_provider`、`storage_url`、`status`、`metadata` 等不存在的字段
- 保存文件使用了正确的相对路径 `default_storage.save("uploads/{filename}", ...)`

**当前视图文件**: `/home/ming/Desktop/统信/小程序/memoryday/backend/apps/upload/views.py`（已同步到服务器）

### 修复 3: 上传目录挂载（待修复）
**发现**: `docker-compose.prod.yml` 中没有为 `memoryday-backend` 容器挂载 media 目录。
Nginx 容器已经从宿主机 `/opt/memoryday/backend/media/` 读取静态文件，但 Django 容器未挂载该目录。

**需要**: 在 `docker-compose.prod.yml` 的 `backend` 服务中添加：
```yaml
volumes:
  - ./backend/media:/app/media
```

### 修复 4: 登录/注册页面（小程序端待确认）
检查点：
1. `pages/login/login.js` — 登录逻辑实现
2. `app.js` 中 `request` 方法 — token 携带和 401 处理
3. 上传页面（`pages/dish-edit/dish-edit.js`）的 `uploadImagesToCos` 方法是否先检查登录状态

## 当前 API 测试验证

所有测试通过 `docker exec memoryday-backend python -c "..."` 在容器内执行。

```bash
# ✅ 健康检查
curl http://localhost/api/health/ → 200 {"status":"healthy",...}

# ✅ 登录（使用 username + password 字段）
curl -X POST http://localhost/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"your-test-phone","password":"your-test-password"}'
→ 返回 access 和 refresh token

# ✅ 上传图片（需 Bearer token）
curl -X POST http://localhost/api/upload/upload/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@real_test.jpg;type=image/jpeg" \
  -F "upload_type=dish_image"
→ 返回文件信息（id, file_url, file_size 等）

# ✅ 通过 Nginx 访问上传的图片
curl -s -o /dev/null -w "HTTP: %{http_code}, Size: %{size_download} bytes\n" \
  http://your-server-ip/media/uploads/<filename>.jpg
→ HTTP: 200
```

## 测试用户凭证
| 字段 | 值 |
|------|-----|
| **手机号** | `your-test-phone` |
| **密码** | `your-test-password` |
| **昵称** | 测试用户 |

## 待完成任务

### 优先级高
- [ ] **`docker-compose.prod.yml` 添加 media 目录挂载**：为 `memoryday-backend` 容器添加 `- ./backend/media:/app/media` 挂载，使上传的文件能够持久化到宿主机并被 Nginx 访问
- [ ] **重启容器**：修改 docker-compose 后 `docker compose -f docker-compose.prod.yml --env-file backend/.env up -d` 重启

### 小程序端待排查
- [ ] **检查登录流程**：确保小程序能正常登录（输入手机号/密码后能获取到 token）
- [ ] **检查 token 存储和携带**：`app.js` 的 `request` 方法是否正确从 `wx.getStorageSync('token')` 读取并加入 header
- [ ] **检查 401 处理**：token 过期或未登录时，小程序应该跳转到登录页面而不是静默失败
- [ ] **检查上传页面**：`pages/dish-edit/dish-edit.js` 中 `uploadImagesToCos` 方法的上传逻辑
- [ ] **排查小程序网络请求**：使用微信开发者工具查看具体请求的错误信息

### 后续改进建议
- [ ] 上传接口应考虑支持匿名/无需认证的上传（或完善注册流程）
- [ ] 添加图片压缩功能，减小传输体积
- [ ] 考虑对接腾讯云 COS 存储（已有 `services/cosService.js` 和 `config/cos.js` 配置）

## 关键文件位置

| 文件 | 本地路径 | 远程路径 |
|------|----------|----------|
| 上传视图 | `backend/apps/upload/views.py` | `/opt/memoryday/backend/apps/upload/views.py` |
| UploadedFile 模型 | `backend/apps/upload/models.py` | `/opt/memoryday/backend/apps/upload/models.py` |
| 用户模型 | `backend/apps/users/models.py` | `/opt/memoryday/backend/apps/users/models.py` |
| 用户视图 | `backend/apps/users/views.py` | `/opt/memoryday/backend/apps/users/views.py` |
| Docker Compose | `docker-compose.prod.yml` | `/opt/memoryday/docker-compose.prod.yml` |
| Dockerfile | `backend/Dockerfile` | `/opt/memoryday/backend/Dockerfile` |
| Nginx 配置 | `backend/docker/nginx/conf.d/memoryday.conf` | `/opt/memoryday/backend/docker/nginx/conf.d/memoryday.conf` |
| 小程序 app.js | `app.js` | N/A (本地开发) |
| 小程序登录页 | `pages/login/login.js` | N/A (本地开发) |
| COS 服务 | `services/cosService.js` | N/A (本地开发/小程序) |

## 管理命令速查

```bash
# SSH 登录
ssh root@your-server-ip  # 密码: your-ssh-password

# 进入后端容器
docker exec -it memoryday-backend bash

# 查看后端日志
docker logs memoryday-backend --tail 50

# 查看 Nginx 日志
docker logs memoryday-nginx --tail 50

# 在容器内执行 Django 管理命令
docker exec -i memoryday-backend python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memoryday_backend.settings.production')
import django; django.setup()
# ... your code ...
"

# 重启后端容器
docker restart memoryday-backend

# 同步文件到容器
docker cp /opt/memoryday/backend/apps/upload/views.py memoryday-backend:/app/apps/upload/views.py

# 重启所有服务
cd /opt/memoryday
docker compose -f docker-compose.prod.yml --env-file backend/.env down
docker compose -f docker-compose.prod.yml --env-file backend/.env up -d
```