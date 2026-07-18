# MemoryDay 项目配置指南

## 概览

`git pull` 拉取代码后，需要按以下步骤配置才能让前端（微信小程序）和后端（Django）正常运行。

---

## 一、后端配置

### 1. 编辑 `backend/.env` 文件

**该文件已提交到 Git（脱敏版本），`git pull` 后已存在。**

只需将 `<your-xxx>` 占位符替换为真实值，无需手动创建文件：

```bash
# ==================== Django 基础配置 ====================
# 必填：生成一个唯一的密钥（可用 openssl rand -hex 32 生成）
DJANGO_SECRET_KEY=your-django-secret-key

# 调试模式：本地开发用 True，生产用 False
DJANGO_DEBUG=False

# 允许访问的主机，逗号分隔
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-server-ip,*

# ==================== MySQL 数据库配置 ====================
MYSQL_DATABASE=memoryday
MYSQL_USER=memoryday_user
MYSQL_PASSWORD=your-db-password
MYSQL_ROOT_PASSWORD=your-db-root-password
MYSQL_HOST=db
MYSQL_PORT=3306

# ==================== Redis 缓存配置 ====================
# 注意：密码需与下方 REDIS_PASSWORD 保持一致
REDIS_URL=redis://:your-redis-password@redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# ==================== Celery 任务队列 ====================
CELERY_BROKER_URL=redis://:your-redis-password@redis:6379/1
CELERY_RESULT_BACKEND=redis://:your-redis-password@redis:6379/2

# ==================== 微信小程序配置 ====================
# 必填：从微信公众平台获取（https://mp.weixin.qq.com）
WECHAT_APPID=your-wechat-appid
WECHAT_SECRET=your-wechat-secret
WECHAT_TOKEN=your-wechat-token
WECHAT_AES_KEY=your-wechat-aes-key

# ==================== 文件上传限制 ====================
MAX_FILE_SIZE=104857600
MAX_STORAGE_PER_USER=10737418240
UPLOAD_DIR=uploads

# ==================== 腾讯云 COS 对象存储（可选）====================
# 如不使用 COS，保持 COS_ENABLED=False 即可
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

# ==================== CORS 跨域配置 ====================
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost,http://127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ==================== 日志配置 ====================
LOG_LEVEL=INFO
LOG_FILE=logs/django.log

# ==================== 部署模式 ====================
DEPLOYMENT_MODE=production

# ==================== 认证方式开关 ====================
# 生产环境关闭密码/短信登录，仅保留微信登录
DISABLE_PASSWORD_LOGIN=True
DISABLE_SMS_LOGIN=True
```

### 2. 上述配置项说明

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `DJANGO_SECRET_KEY` | Django 签名密钥 | 运行 `openssl rand -hex 32` 生成 |
| `MYSQL_PASSWORD` | MySQL 数据库用户密码 | 自行设置 |
| `MYSQL_ROOT_PASSWORD` | MySQL root 密码 | 自行设置 |
| `REDIS_PASSWORD` | Redis 密码 | 自行设置 |
| `WECHAT_APPID` | 微信小程序 AppID | [微信公众平台](https://mp.weixin.qq.com) → 设置与开发 → 基本配置 |
| `WECHAT_SECRET` | 微信小程序 AppSecret | [微信公众平台](https://mp.weixin.qq.com) → 设置与开发 → 基本配置 |
| `COS_SECRET_ID` | 腾讯云 API 密钥 ID | [腾讯云 API 密钥管理](https://console.cloud.tencent.com/cam/capi) |
| `COS_SECRET_KEY` | 腾讯云 API 密钥 Key | [腾讯云 API 密钥管理](https://console.cloud.tencent.com/cam/capi) |

---

## 二、小程序前端配置

### 2.1 `project.config.json`（微信开发者工具配置）

**该文件已被 `.gitignore` 忽略，需要手动创建。**

```json
{
  "description": "项目配置文件",
  "setting": {
    "urlCheck": false,
    "es6": true,
    "enhance": true,
    "postcss": true,
    "minified": true,
    "minifyWXSS": true,
    "minifyWXML": true,
    "ignoreUploadUnusedFiles": true
  },
  "compileType": "miniprogram",
  "libVersion": "2.31.0",
  "appid": "your-wechat-appid",
  "projectname": "MemoryDay",
  "simulatorType": "wechat",
  "simulatorPluginLibVersion": {}
}
```

> **注意**：`appid` 必须与 `backend/.env` 中的 `WECHAT_APPID` 保持一致。

### 2.2 `app.js` — 配置 API 地址

打开 `app.js`，找到 `globalData` 中的 `baseUrl` 和 `localApiUrl`，修改为你的后端服务器地址：

```javascript
globalData: {
    baseUrl: 'http://your-server-ip/api',   // 后端 API 地址
    localApiUrl: 'http://your-server-ip/api', // 后端 API 地址
    // ...
}
```

需要修改的字段（共 4 处）：
- **第 42 行**：`baseUrl: 'http://your-server-ip/api'`
- **第 46 行**：`localApiUrl: 'http://your-server-ip/api'`
- **第 365 行附近**：`this.globalData.baseUrl = 'http://your-server-ip/api'`

### 2.3 其他前端文件中的 API 地址

以下文件也包含硬编码的 API 地址，需要根据你的服务器修改：

| 文件 | 行号 | 需要修改的内容 |
|------|------|---------------|
| `miniprogram/app.js` | 第 30 行 | `baseUrl: 'http://your-server-ip/api'` |
| `utils/deployment.js` | 第 40-41 行 | `description` 和 `apiUrl` |
| `pages/deployment/deployment.js` | 第 23-24 行 | `description` 和 `apiUrl` |
| `pages/deployment/deployment.wxml` | 第 72 行 | 服务器 IP 描述 |
| `services/cosService.js` | 第 160 行 | `baseUrl` 后备地址 |

> **建议**：后续可优化为统一从 `config/config.js` 或 `app.globalData` 读取 API 地址，避免多处硬编码。

---

## 三、使用 Docker 部署后端

### 3.1 本地开发环境

```bash
# 使用本地开发配置
docker compose -f docker-compose.yml --env-file backend/.env up -d
```

### 3.2 生产环境

```bash
# 使用生产环境配置（禁用 SSL 重定向等）
docker compose -f docker-compose.prod.yml --env-file backend/.env up -d
```

### 3.3 初始化数据库

```bash
# 执行数据库迁移
docker exec memoryday-backend python manage.py migrate

# 创建测试用户（可选）
docker exec memoryday-backend python manage.py shell -c "
from apps.users.models import User
User.objects.create_user(phone='your-test-phone', password='your-test-password', nickname='测试用户', is_active=True)
print('测试用户创建成功')
"
```

---

## 四、配置清单总表

### 首次部署必须配置的项

| # | 文件 | 配置项 | 状态 |
|---|------|--------|------|
| 1 | `backend/.env` | 所有环境变量（需手动创建） | ⚠️ 必填 |
| 2 | `project.config.json` | `appid`（需手动创建） | ⚠️ 必填 |
| 3 | `app.js` | `baseUrl` / `localApiUrl`（修改 4 处） | ⚠️ 必填 |
| 4 | `miniprogram/app.js` | `baseUrl` | ⚠️ 必填 |
| 5 | `utils/deployment.js` | `apiUrl` | ⚠️ 必填 |
| 6 | `pages/deployment/deployment.js` | `apiUrl` | ⚠️ 必填 |
| 7 | `services/cosService.js` | `baseUrl` 后备地址 | ⚠️ 必填 |

### 可选配置项

| # | 文件 | 配置项 | 状态 |
|---|------|--------|------|
| 8 | `backend/.env` | COS 相关配置（COS_SECRET_ID 等） | 可选 |
| 9 | `backend/.env` | `CORS_ALLOWED_ORIGINS` | 按需修改 |
| 10 | `backend/.env` | `DISABLE_PASSWORD_LOGIN` / `DISABLE_SMS_LOGIN` | 按需修改 |

---

## 五、安全提醒

1. **`backend/.env`** 和 **`project.config.json`** 已提交到 Git（内容已脱敏，均为占位符），**请务必替换为真实值后再使用**
2. **`.credentials`** 仍被 `.gitignore` 忽略，不会提交到 Git（本地保管）
3. 请勿将真实的 `WECHAT_SECRET`、`COS_SECRET_KEY`、数据库密码等直接提交到 Git
4. 定期更换密钥和密码
5. 生产环境建议配置 HTTPS（使用 Certbot + Let's Encrypt）

---

## 六、验证流程

### 后端验证

```bash
# 健康检查
curl http://your-server-ip/api/health/

# 登录测试
curl -X POST http://your-server-ip/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"your-test-phone","password":"your-test-password"}'

# 上传测试
curl -X POST http://your-server-ip/api/upload/upload/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@test.jpg;type=image/jpeg" \
  -F "upload_type=dish_image"
```

### 前端验证

1. 在微信开发者工具中打开项目（确保 `project.config.json` 已配置正确 `appid`）
2. 检查 `app.js` 中的 API 地址是否正确
3. 点击登录按钮，应能正常跳转到微信授权页面
4. 登录后能正常浏览和上传图片