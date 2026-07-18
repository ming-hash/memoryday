# MemoryDay 文件上传方案说明

## 概述

MemoryDay 项目支持 **两种文件上传方案**，前端代码根据环境自动选择：

| 方案 | 存储位置 | 优先级 | 当前状态 |
|------|---------|--------|---------|
| **方案A：腾讯云 COS 对象存储** | 腾讯云 COS 存储桶 | 优先（优先尝试） | ⚠️ 代码保留，但未启用 |
| **方案B：本地 Django 服务器存储** | 服务器 `backend/media/` 目录 | 降级（COS 失败时自动切换） | ✅ 当前实际使用 |

---

## 方案A：腾讯云 COS 对象存储

### 架构

```
小程序前端                   Django 后端                    腾讯云 COS
   │                           │                              │
   ├─ POST /cos/sts-token/ ───→│                              │
   │                           ├─ 生成 STS 临时凭证 ──────────→│
   │←── STS 凭证 ──────────────┤                              │
   │                           │                              │
   ├─ cos.postObject() ──────────────────────────────────────→│
   │←── 上传成功 + 图片 URL ─────────────────────────────────│
   │                           │                              │
   ├─ POST /cos/signed-url/ ──→│                              │
   │                           ├─ 生成签名 URL ──────────────→│
   │←── 签名 URL ──────────────┤                              │
```

### 涉及的文件

| 文件 | 作用 |
|------|------|
| `config/cos.js` | COS 存储桶配置（地域、Bucket 名、签名 URL 开关等） |
| `services/cosService.js` | 前端 COS 上传服务（COS 上传 + 本地降级） |
| `backend/apps/cos/` | 后端 COS 相关 API（STS 凭证、签名 URL 等） |
| `backend/.env`（COS 相关配置段） | COS 密钥、存储桶等环境变量 |

### 配置步骤

#### 1. 腾讯云侧准备

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 进入 [COS 控制台](https://console.cloud.tencent.com/cos) → 创建存储桶（如 `memoryday-1259810697`，地域 `ap-beijing`，权限建议**私有读写**）
3. 进入 [访问管理 → API 密钥管理](https://console.cloud.tencent.com/cam/capi) → 新建密钥，获取 `SecretId` 和 `SecretKey`

#### 2. 后端配置（`backend/.env`）

```bash
# 启用 COS
COS_ENABLED=True

# 腾讯云 API 密钥
COS_SECRET_ID=your-cos-secret-id
COS_SECRET_KEY=your-cos-secret-key

# 存储桶信息
COS_BUCKET=memoryday-1259810697
COS_REGION=ap-beijing
COS_APP_ID=1259810697

# 签名 URL（私有读写存储桶需要）
COS_USE_SIGNED_URL=True
COS_DEFAULT_EXPIRES=3600
```

#### 3. 前端配置（`config/cos.js`）

```javascript
const STORAGE_SUFFIX = '1259810697'  // 改为你的 APPID
const BUCKET_NAME = `memoryday-${STORAGE_SUFFIX}`
```

#### 4. 微信小程序后台配置域名

在 [微信公众平台](https://mp.weixin.qq.com/) → 开发管理 → 开发设置 → 服务器域名：

| 类型 | 域名 |
|------|------|
| uploadFile 合法域名 | `https://memoryday-1259810697.cos.ap-beijing.myqcloud.com` |
| downloadFile 合法域名 | `https://memoryday-1259810697.cos.ap-beijing.myqcloud.com` |

#### 5. 验证

```bash
# 后端检查 COS 配置状态
docker exec memoryday-backend python manage.py cos_status
```

### 适用场景

- 图片量大、需要 CDN 加速分发
- 多服务器部署，需要统一存储层
- 希望降低服务器磁盘 I/O 压力

---

## 方案B：本地 Django 服务器存储（当前使用）

### 架构

```
小程序前端                   Django 后端
   │                           │
   ├─ POST /api/upload/upload/ │
   │   (multipart/form-data)   │
   │   + Authorization: Bearer │
   │                           ├─ 校验 Token
   │                           ├─ 保存文件到 /app/media/uploads/
   │                           ├─ 记录到数据库
   │←── 返回 file_url ────────┤
   │                           │
   ├─ GET /media/uploads/xxx   │
   │←── Nginx 直接返回文件 ────│
```

### 涉及的文件

| 文件 | 作用 |
|------|------|
| `services/cosService.js`（`uploadImageToLocal()` 方法） | 前端本地上传逻辑（实为降级方案，但当前为主要方案） |
| `backend/apps/upload/` | 后端上传 API（`/api/upload/upload/`） |
| `backend/media/` | 文件存储目录（Docker 卷挂载持久化） |
| `backend/.env`（上传配置段） | 文件大小限制、存储目录等 |

### 配置步骤

#### 1. 后端配置（`backend/.env`）

```bash
# 确保 COS 未启用
COS_ENABLED=False

# 文件上传限制
MAX_FILE_SIZE=104857600           # 单文件最大 100MB
MAX_STORAGE_PER_USER=10737418240  # 每用户最大 10GB
UPLOAD_DIR=uploads
```

#### 2. Docker 卷持久化

`docker-compose.prod.yml` 中已配置 media 目录持久化：

```yaml
volumes:
  - ./backend/media:/app/media
```

确保宿主机 `backend/media/` 目录存在且可写。

#### 3. 小程序后端 API 地址配置

修改 `app.js` 中的 `globalData.baseUrl` 为你的服务器地址：

```javascript
globalData: {
  baseUrl: 'http://your-server-ip/api',  // 改为实际服务器 IP 或域名
  localApiUrl: 'http://your-server-ip/api',
}
```

> 注意：小程序端需在微信公众平台配置 `request` 合法域名为此地址。

#### 4. Nginx 静态文件服务

`docker-compose.prod.yml` 中的 Nginx 已配置 `/media/` 路由：

```nginx
location /media/ {
    alias /app/media/;
    expires 7d;
    add_header Cache-Control "public";
}
```

### 适用场景

- 单服务器部署，文件量适中
- 不需要 CDN 加速
- 希望简化架构，减少外部依赖
- **当前项目的实际运行方式**

---

## 上传流程详解（代码层面）

前端 `CosService` 上传逻辑如下：

```
uploadImage(filePath)          ← 入口
  │
  ├─ 尝试 COS 上传
  │   ├─ getStsToken()         → POST /cos/sts-token/  获取临时凭证
  │   ├─ cos.postObject()      → 上传到腾讯云 COS
  │   └─ 成功 → 返回 COS 图片 URL
  │
  └─ 捕获异常 → 自动降级
      └─ uploadImageToLocal()  → POST /api/upload/upload/  上传到 Django 服务器
                                  └─ 返回后端图片 URL
```

**当前实际运行路径**：因 `COS_ENABLED=False`，后端 `/cos/sts-token/` 端点不可用，COS 上传阶段会抛出异常，**自动降级到本地 Django 存储**。用户无感知，上传功能正常。

---

## 切换方案

### 从方案B（本地存储）切换到方案A（COS）

1. 按上方"方案A 配置步骤"完成配置
2. 将 `backend/.env` 中 `COS_ENABLED` 设为 `True`，填写真实密钥
3. 重启后端容器：`docker compose -f docker-compose.prod.yml --env-file backend/.env restart backend`
4. 验证：通过小程序上传图片，观察控制台日志应显示 "COS 上传成功"

### 从方案A（COS）切换到方案B（本地存储）

1. 将 `backend/.env` 中 `COS_ENABLED` 设为 `False`
2. 重启后端容器
3. COS 上传失败后自动降级到本地存储，无需修改前端代码

---

## 两种方案的对比

| 对比项 | COS 对象存储 | 本地 Django 存储 |
|--------|-------------|-----------------|
| **存储位置** | 腾讯云 COS 存储桶 | 服务器本地磁盘 |
| **访问速度** | CDN 加速，全球访问快 | 依赖服务器带宽 |
| **存储成本** | 按量付费（存储 + 流量） | 仅占用服务器磁盘 |
| **流量成本** | COS 下行流量收费 | 服务器带宽（已固定付费） |
| **扩展性** | 无限容量，自动扩展 | 受限于服务器磁盘大小 |
| **运维复杂度** | 需要管理 COS 密钥和权限 | 简单，Docker 卷自动持久化 |
| **图片处理** | 内置图片处理（缩略图、裁剪等） | 需自行实现 |
| **依赖** | 腾讯云账号 + 网络可达 | 无外部依赖 |
| **当前状态** | 代码保留，未启用 | ✅ 正在使用 |

---

## 常见问题

### Q: 为什么上传图片时控制台先报 COS 错误，然后上传成功？

这是正常的。前端逻辑是**优先尝试 COS，失败后自动降级到本地**。当前 COS 未配置，所以：
1. 先尝试 COS 上传 → 失败（日志报错）
2. 自动降级到本地 Django 上传 → 成功（用户无感知）

如果希望去掉报错日志，将来可以移除 `uploadImage()` 中的 COS 尝试逻辑，直接调用 `uploadImageToLocal()`。

### Q: 如果将来想用 COS，需要改代码吗？

**不需要改前端代码**。只需：
1. 配置 COS 密钥和存储桶
2. 将 `COS_ENABLED` 设为 `True`
3. 确保后端 `/cos/sts-token/` 端点正常
4. 前端会自动优先使用 COS 上传

### Q: 两种方案的文件可以共存吗？

技术上可以，但**不推荐**。同时启用会导致：
- 部分图片存在 COS，部分存在本地，管理混乱
- 图片 URL 格式不一致，前端需要兼容两种格式