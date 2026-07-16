# MemoryDay 小程序部署指南

本文档详细说明 MemoryDay 小程序项目的完整部署流程，包括前端小程序、后端Django服务以及腾讯云COS存储服务的配置和部署。

## 一、项目架构概述

MemoryDay 是一个记录日常饮食的小程序应用，包含以下组件：

- **前端**: 微信小程序，使用原生小程序框架
- **后端**: Django REST Framework API服务
- **存储**: 腾讯云COS对象存储服务
- **数据库**: MySQL/PostgreSQL
- **缓存**: Redis

## 二、环境准备

### 2.1 腾讯云账号准备

1. **注册腾讯云账号**
   - 访问 [腾讯云官网](https://cloud.tencent.com/)
   - 完成实名认证

2. **开通COS服务**
   - 进入 [COS控制台](https://console.cloud.tencent.com/cos)
   - 点击"创建存储桶"

### 2.2 创建存储桶

#### 开发环境存储桶
- **存储桶名称**: `memoryday-dev-{appid}` (替换为实际小程序AppID)
- **地域**: `ap-beijing` (北京)
- **访问权限**: 公有读私有写
- **版本控制**: 开启（可选）

#### 生产环境存储桶
- **存储桶名称**: `memoryday-prod-{appid}`
- **地域**: `ap-beijing`
- **访问权限**: 公有读私有写
- **版本控制**: 开启

### 2.3 获取API密钥

1. 进入 [访问管理控制台](https://console.cloud.cent.com/cam)
2. 选择"访问密钥" -> "API密钥管理"
3. 点击"新建密钥"，记录以下信息：
   - `COS_SECRET_ID`
   - `COS_SECRET_KEY`

### 2.4 配置微信小程序

1. **申请小程序AppID**
   - 访问 [微信公众平台](https://mp.weixin.qq.com/)
   - 注册小程序并获取AppID

2. **配置服务器域名**
   - request合法域名: 后端API服务域名
   - uploadFile合法域名: COS存储桶域名
   - downloadFile合法域名: COS存储桶域名

## 三、配置文件设置

### 3.1 环境变量配置

复制 `backend/.env.example` 为 `backend/.env` 并填写实际配置：

```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
MYSQL_DATABASE=memoryday
MYSQL_USER=memoryday_user
MYSQL_PASSWORD=your-mysql-password
MYSQL_HOST=localhost
MYSQL_PORT=3306

# Redis
REDIS_URL=redis://localhost:6379/0

# WeChat Mini Program
WECHAT_APPID=your-wechat-appid
WECHAT_SECRET=your-wechat-secret
WECHAT_TOKEN=your-wechat-token
WECHAT_AES_KEY=your-wechat-aes-key

# Tencent Cloud COS Configuration (已集成完成)
COS_ENABLED=True
COS_SECRET_ID=your-cos-secret-id
COS_SECRET_KEY=your-cos-secret-key
COS_BUCKET=your-cos-bucket-name
COS_REGION=ap-beijing
COS_APP_ID=your-cos-app-id
COS_DOMAIN=your-cos-domain.com
COS_PREFIX=memoryday
COS_MAX_FILE_SIZE=5242880  # 5MB
COS_ALLOWED_TYPES=image/jpeg,image/png,image/gif,image/webp
```

### 3.2 后端Django配置（已集成完成）

项目已完成以下配置集成：

- **COS服务类**: `apps/cos/services.py` - 完整的COS文件操作服务
- **API视图**: `apps/cos/views.py` - REST API接口，支持文件上传、下载、删除、列表
- **模型序列化**: `apps/cos/serializers.py` - 文件元数据序列化
- **URL路由**: `apps/cos/urls.py` - API路由配置
- **管理命令**: `apps/cos/management/commands/cos_status.py` - COS状态检查命令

### 3.3 前端小程序配置

已完成的修改：

1. **COS服务封装**: `services/cosService.js` - 完整的COS上传服务
2. **图片上传适配**: `pages/dish-edit/dish-edit.js` - 集成COS上传逻辑
3. **配置管理**: `config/cos.js` - COS配置管理
4. **安装脚本**: `scripts/install-cos-sdk.js` - 自动安装COS SDK

## 三、小程序前端配置

### 3.1 安装COS SDK

在项目根目录执行：

```bash
npm install cos-wx-sdk-v5
```

### 3.2 配置安全域名

在微信小程序后台配置：

1. **request合法域名**:
   - `https://your-backend-domain.com`

2. **uploadFile合法域名**:
   - `https://memoryday-dev-{appid}.cos.ap-beijing.myqcloud.com`
   - `https://memoryday-prod-{appid}.cos.ap-beijing.myqcloud.com`

3. **downloadFile合法域名**:
   - 同上COS域名

### 3.3 修改图片上传逻辑

已完成的修改：

1. **services/cosService.js** - COS服务封装
2. **pages/dish-edit/dish-edit.js** - 图片上传适配

## 四、部署流程

### 4.1 开发环境部署

#### 前端部署（微信小程序）
1. **导入项目**
   - 打开微信开发者工具
   - 导入项目目录 `c:/Users/ming_/Desktop/memoryday`
   - 配置正确的AppID

2. **环境配置**
   - 修改 `config/env.js` 中的环境变量
   - 配置后端API地址
   - 配置COS存储桶信息

3. **编译测试**
   - 点击"编译"按钮
   - 测试图片上传功能
   - 验证数据同步

#### 后端部署（Django）
1. **安装依赖**：
   ```bash
   cd backend
   pip install -r requirements.txt
   # COS SDK已包含在requirements.txt中
   ```

2. **环境配置**
   ```bash
   # 复制环境变量文件
   cp .env.example .env
   # 编辑.env文件，填写实际配置
   ```

3. **数据库迁移**：
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **启动服务**：
   ```bash
   # 开发环境
   python manage.py runserver
   
   # 或使用生产脚本
   python start_server.py
   ```

5. **验证COS配置**：
   ```bash
   python manage.py cos_status
   ```

### 4.2 生产环境部署

#### 服务器要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+
- **Python**: 3.8+
- **数据库**: MySQL 8.0+ / PostgreSQL 12+
- **内存**: 2GB+
- **存储**: 20GB+ SSD

#### 部署方式一：传统服务器部署

1. **服务器准备**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3-pip python3-venv nginx mysql-server redis-server
   
   # CentOS/RHEL
   sudo yum update -y
   sudo yum install python3-pip python3-venv nginx mysql-server redis
   ```

2. **项目部署**
   ```bash
   # 克隆代码
   git clone https://github.com/your-repo/memoryday.git
   cd memoryday/backend
   
   # 创建虚拟环境
   python3 -m venv venv
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   pip install gunicorn
   
   # 配置环境变量
   cp .env.example .env
   # 编辑.env文件，设置生产环境配置
   
   # 数据库设置
   python manage.py migrate
   python manage.py collectstatic
   ```

3. **Gunicorn配置**
   创建 `gunicorn.conf.py`：
   ```python
   bind = "127.0.0.1:8000"
   workers = 3
   worker_class = "sync"
   timeout = 120
   max_requests = 1000
   max_requests_jitter = 100
   ```

4. **Nginx配置**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       location /static/ {
           alias /path/to/memoryday/backend/static/;
           expires 30d;
           add_header Cache-Control "public, immutable";
       }
       
       location /media/ {
           alias /path/to/memoryday/backend/media/;
           expires 7d;
           add_header Cache-Control "public";
       }
   }
   ```

5. **服务管理**
   创建systemd服务文件 `/etc/systemd/system/memoryday.service`：
   ```ini
   [Unit]
   Description=MemoryDay Django Application
   After=network.target
   
   [Service]
   Type=simple
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/memoryday/backend
   ExecStart=/path/to/memoryday/backend/venv/bin/gunicorn memoryday_backend.wsgi:application -c gunicorn.conf.py
   ExecReload=/bin/kill -s HUP $MAINPID
   Restart=on-failure
   
   [Install]
   WantedBy=multi-user.target
   ```

#### 部署方式二：Docker部署

1. **准备Docker环境**
   ```bash
   # 安装Docker和Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **使用Docker Compose**
   项目根目录已提供 `docker-compose.yml`：
   ```bash
   docker-compose up -d
   ```

3. **环境配置**
   ```bash
   # 复制环境变量
   cp .env.example .env
   # 编辑.env文件
   
   # 启动服务
   docker-compose up -d
   
   # 执行数据库迁移
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py collectstatic
   ```

## 五、测试验证

### 5.1 功能测试清单

#### 后端API测试
- [ ] COS配置状态检查: `python manage.py cos_status`
- [ ] 文件上传API测试
- [ ] 文件下载API测试
- [ ] 文件列表API测试
- [ ] 文件删除API测试
- [ ] STS临时凭证获取API测试

#### 前端功能测试
- [ ] 图片选择功能正常
- [ ] 图片上传到COS成功
- [ ] 图片URL正确显示
- [ ] 图片删除功能正常
- [ ] 大文件上传限制（5MB）
- [ ] 文件类型验证（jpg/png/gif/webp）
- [ ] 网络异常处理

### 5.2 性能测试

1. **上传速度测试**
   - 单张图片（1MB）上传时间 < 3秒
   - 多张图片并发上传（3张同时上传）
   - 大文件上传（5MB限制内）

2. **加载速度测试**
   - COS图片加载时间 < 1秒
   - CDN加速效果验证（如启用）

3. **API响应测试**
   - 文件列表API响应时间 < 200ms
   - STS凭证获取响应时间 < 500ms

### 5.3 使用测试工具

项目提供了以下测试工具：

```bash
# COS配置检查
python scripts/check_cos_config.py

# 后端API测试
python manage.py test apps.cos

# 前端COS服务测试
# 在微信开发者工具中运行测试用例
```

## 六、故障排除

### 6.1 常见问题

#### 问题1: STS token获取失败
**原因**: 权限配置错误或密钥无效
**解决**: 
1. 检查SecretId/SecretKey是否正确
2. 验证COS存储桶权限
3. 检查后端API是否正常

#### 问题2: 图片上传失败
**原因**: 网络问题或文件大小超限
**解决**:
1. 检查网络连接
2. 验证文件大小限制
3. 检查COS存储桶空间

#### 问题3: 图片显示异常
**原因**: URL格式错误或CDN配置问题
**解决**:
1. 检查图片URL格式
2. 验证COS存储桶公有读权限
3. 检查CDN配置

### 6.2 日志查看

#### 前端日志
```javascript
// 开启调试模式
wx.setEnableDebug({
    enableDebug: true
})
```

#### 后端日志
```bash
# 查看Django日志
tail -f /var/log/django.log

# 查看Nginx日志
tail -f /var/log/nginx/error.log
```

## 七、最佳实践

### 7.1 安全性

1. **密钥管理**
   - 使用环境变量存储敏感信息
   - 定期更换API密钥
   - 使用STS临时凭证

2. **权限控制**
   - 最小权限原则
   - 定期审计权限配置
   - 使用存储桶策略

### 7.2 性能优化

1. **图片优化**
   - 使用WebP格式
   - 合理设置图片质量
   - 启用CDN加速

2. **缓存策略**
   - 设置合适的缓存头
   - 使用浏览器缓存
   - CDN缓存配置

### 7.3 成本控制

1. **存储优化**
   - 定期清理无用文件
   - 使用生命周期规则
   - 选择合适的存储类型

2. **流量优化**
   - 启用CDN减少回源流量
   - 压缩图片减少流量消耗
   - 使用合适的存储地域

## 八、扩展功能

### 8.1 图片处理

腾讯云COS支持丰富的图片处理功能：

```javascript
// 缩略图
const thumbnailUrl = imageUrl + '?imageView2/1/w/200/h/200'

// 质量压缩
const compressedUrl = imageUrl + '?imageView2/0/q/75'

// 格式转换
const webpUrl = imageUrl + '?imageMogr2/format/webp'
```

### 8.2 视频处理

如需支持视频上传，可扩展COS服务：

```python
# 后端添加视频处理
class VideoProcessor:
    def process_video(self, file_key):
        # 使用腾讯云视频处理服务
        pass
```

## 九、技术支持

- **腾讯云文档**: [COS开发者指南](https://cloud.tencent.com/document/product/436)
- **微信小程序文档**: [文件上传](https://developers.weixin.qq.com/miniprogram/dev/api/media/image/wx.chooseImage.html)
- **问题反馈**: 创建GitHub Issue

## 十、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2025-01-24 | 初始版本，支持COS图片上传 |
| v1.1 | 2025-02-01 | 添加图片处理功能 |

---

**注意**: 部署前请确保已阅读并理解所有配置项，生产环境部署前务必进行充分测试。