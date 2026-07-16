# MemoryDay - 今日吃啥小程序

一个基于微信小程序的个人菜谱管理应用，帮助用户记录、管理和随机选择每日饮食。项目已集成腾讯云COS对象存储服务，支持图片上传和云端存储。

## 🎯 项目特色

- 🍽️ 个人菜谱管理：添加、编辑、删除个人菜品
- 🎲 随机选择：一键随机选择今日吃什么
- 📊 饮食统计：查看个人饮食偏好和统计
- 🏷️ 智能分类：支持多标签分类和搜索
- 📱 微信小程序：原生微信小程序体验
- 🔒 用户系统：完整的用户认证和权限管理
- ☁️ 腾讯云COS：云端图片存储和CDN加速

## 🛠️ 技术栈

### 前端 (微信小程序)
- WXML + WXSS + JavaScript
- 微信小程序原生框架
- 组件化开发
- 响应式设计
- 腾讯云COS SDK

### 后端 (Django REST Framework)
- Python 3.8+
- Django 4.2
- Django REST Framework
- JWT 认证
- SQLite (开发) / MySQL (生产)
- CORS 支持
- 腾讯云COS Python SDK

### 云服务
- 腾讯云对象存储 (COS)
- 腾讯云访问管理 (CAM)
- STS临时凭证服务

## 📁 项目结构

```
memoryday/
├── backend/                 # Django 后端项目
│   ├── memoryday_backend/   # Django 项目配置
│   ├── apps/               # Django 应用
│   │   ├── users/          # 用户管理
│   │   ├── dishes/         # 菜品管理
│   │   ├── tags/           # 标签管理
│   │   ├── stats/          # 统计功能
│   │   ├── upload/         # 文件上传
│   │   └── cos/            # 腾讯云COS集成 ✅
│   ├── scripts/            # 部署和配置脚本
│   ├── docker/             # Docker配置文件
│   ├── requirements.txt    # Python 依赖
│   ├── requirements-cos.txt # COS相关依赖
│   ├── Dockerfile          # Docker镜像构建
│   ├── docker-compose.yml  # Docker Compose配置
│   ├── setup.py           # 项目安装脚本
│   └── start_server.py    # 开发服务器启动脚本
├── frontend/               # 微信小程序前端
│   ├── pages/              # 小程序页面
│   ├── components/         # 自定义组件
│   ├── services/           # 服务层
│   │   └── cosService.js  # COS服务封装 ✅
│   ├── config/             # 配置文件
│   │   └── cos.js         # COS配置管理 ✅
│   ├── utils/              # 工具函数
│   └── app.json           # 小程序配置
├── DEPLOYMENT_GUIDE.md     # 详细部署指南 ✅
└── README.md              # 项目说明
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+
- MySQL 5.7+ 或 PostgreSQL 12+
- Redis (可选，用于缓存)
- 微信开发者工具
- 腾讯云账号 (用于COS服务)

### 后端设置

1. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   # 如果需要COS功能，安装额外依赖
   pip install -r requirements-cos.txt
   ```

2. **环境配置**
   ```bash
   # 复制环境变量文件
   cp .env.example .env
   # 编辑 .env 文件配置数据库、COS等设置
   ```

3. **数据库迁移**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **创建超级用户**
   ```bash
   python manage.py createsuperuser
   ```

5. **验证COS配置**
   ```bash
   # 检查COS配置状态
   python manage.py cos_status
   # 或使用快速检查工具
   python scripts/quick_check.py
   ```

6. **启动开发服务器**
   ```bash
   python manage.py runserver
   # 或使用生产启动脚本
   python start_server.py
   ```

### 前端设置

1. **微信开发者工具**
   - 下载并安装微信开发者工具
   - 导入项目根目录作为小程序项目
   - 配置 appid (测试可使用测试号)

2. **配置API地址和COS**
   ```javascript
   // 在 config/env.js 中配置后端API地址和COS信息
   const API_BASE_URL = 'http://127.0.0.1:8000/api';
   const COS_CONFIG = {
     bucket: 'your-bucket-name',
     region: 'ap-beijing',
     prefix: 'memoryday'
   };
   ```

3. **安装COS SDK**
   ```bash
   # 项目已集成COS SDK，无需额外安装
   # 如果遇到问题，运行安装脚本
   node scripts/install-cos-sdk.js
   ```

4. **编译运行**
   - 在微信开发者工具中点击"编译"
   - 确保后端服务正在运行
   - 测试图片上传功能

## 📊 API 接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出

### 菜品接口
- `GET /api/dishes/` - 获取菜品列表
- `POST /api/dishes/` - 创建菜品
- `GET /api/dishes/random` - 随机菜品
- `GET /api/dishes/search` - 搜索菜品

### 标签接口
- `GET /api/tags/` - 获取标签列表
- `GET /api/tags/popular` - 热门标签

### 统计接口
- `GET /api/stats/dashboard` - 用户仪表盘
- `GET /api/stats/global` - 全局统计

### COS文件接口 ✅
- `GET /api/cos/status/` - 获取COS服务状态
- `POST /api/cos/sts/` - 获取STS临时凭证
- `POST /api/cos/upload/` - 文件上传
- `GET /api/cos/files/` - 获取文件列表
- `GET /api/cos/files/{file_key}/` - 获取文件信息
- `DELETE /api/cos/files/{file_key}/` - 删除文件
- `POST /api/cos/files/{file_key}/copy/` - 复制文件
- `GET /api/cos/bucket/info/` - 获取存储桶信息

## 🔧 开发脚本和部署工具

### 环境检查
```bash
# 快速环境检查
cd backend
python scripts/quick_check.py

# 详细环境检查
python scripts/check_environment.py

# COS配置检查
python manage.py cos_status
```

### 部署脚本
```bash
# Linux/Unix 部署
cd backend
chmod +x scripts/deploy.sh
./scripts/deploy.sh deploy

# Windows 部署 (PowerShell)
cd backend\scripts
.\deploy.ps1 -Action deploy

# 更新部署
./scripts/deploy.sh update
# 或
.\deploy.ps1 -Action update
```

### Docker 部署
```bash
# 使用 Docker Compose
cd backend
docker-compose up -d

# 执行数据库迁移
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f web
```

### 开发服务器
```bash
# 开发环境
python manage.py runserver

# 生产启动脚本
python start_server.py
```

## 📝 环境变量配置

创建 `backend/.env` 文件并配置（基于 `.env.example`）：

### 基础配置
```ini
# Django 设置
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# 数据库设置
MYSQL_DATABASE=memoryday
MYSQL_USER=memoryday_user
MYSQL_PASSWORD=your-mysql-password
MYSQL_HOST=localhost
MYSQL_PORT=3306

# Redis (可选)
REDIS_URL=redis://localhost:6379/0
```

### 腾讯云COS配置 ✅
```ini
# COS服务开关
COS_ENABLED=True

# 腾讯云API密钥
COS_SECRET_ID=your-cos-secret-id
COS_SECRET_KEY=your-cos-secret-key

# 存储桶配置
COS_BUCKET=your-cos-bucket-name
COS_REGION=ap-beijing
COS_APP_ID=your-cos-app-id
COS_DOMAIN=your-cos-domain.com

# 文件上传配置
COS_PREFIX=memoryday
COS_MAX_FILE_SIZE=5242880  # 5MB
COS_ALLOWED_TYPES=image/jpeg,image/png,image/gif,image/webp
```

### 微信小程序配置
```ini
# 小程序配置
WECHAT_APPID=your-wechat-appid
WECHAT_SECRET=your-wechat-secret
WECHAT_TOKEN=your-wechat-token
WECHAT_AES_KEY=your-wechat-aes-key
```

### 生产环境配置示例
```ini
# 生产环境配置
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# 生产数据库
MYSQL_HOST=production-db-host
MYSQL_PASSWORD=production-password

# 生产COS配置
COS_BUCKET=memoryday-prod-1250000000
COS_DOMAIN=cdn.your-domain.com
```

## 🐛 常见问题

### 基础问题

1. **端口占用**
   ```bash
   # Linux/Unix
   lsof -i :8000
   # Windows
   netstat -ano | findstr :8000
   ```

2. **数据库连接错误**
   - 检查数据库服务是否启动
   - 确认数据库配置正确
   - 验证数据库用户权限

3. **跨域问题**
   - 确保 CORS 配置正确
   - 检查前端请求地址
   - 验证Nginx代理配置

### COS相关问题 ✅

4. **COS服务连接失败**
   ```bash
   # 检查COS配置
   python manage.py cos_status
   
   # 验证环境变量
   python scripts/quick_check.py
   ```
   - 检查SecretId/SecretKey是否正确
   - 验证存储桶权限设置
   - 确认地域和存储桶名称匹配

5. **图片上传失败**
   - 检查文件大小是否超过限制（5MB）
   - 验证文件类型是否支持（jpg/png/gif/webp）
   - 检查网络连接和COS服务状态

6. **STS凭证获取失败**
   - 验证后端API服务是否正常运行
   - 检查COS权限策略配置
   - 确认时间同步（服务器时间需准确）

### 部署问题

7. **Docker容器启动失败**
   ```bash
   # 查看容器日志
   docker-compose logs -f web
   
   # 检查环境变量
   docker-compose exec web env | grep COS
   ```

8. **权限问题**
   - 确保日志、静态文件目录有写权限
   - 检查Docker卷挂载权限
   - 验证系统服务用户权限

### 调试工具

使用项目提供的调试工具：
```bash
# 详细环境检查
python scripts/check_environment.py

# API健康检查
curl http://localhost:8000/api/health/

# COS服务测试
curl http://localhost:8000/api/cos/status/
```

## 🚀 部署指南

项目提供多种部署方式，详细说明请查看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)。

### 部署方式

1. **本地Docker部署（推荐用于开发）** ✅
   - 使用Docker容器运行全套服务
   - 包含MySQL数据库、Redis缓存
   - 支持热重载开发模式
   - 一键启动，无需复杂配置

2. **腾讯云CloudBase部署（推荐用于生产）** ✅
   - 一键部署后端API服务到云函数
   - 自动配置微信小程序集成
   - 支持弹性伸缩和高可用性
   - 无需管理服务器，免运维

3. **本地生产环境部署**
   - 完整生产环境配置
   - 包含Nginx反向代理
   - 支持SSL证书配置

4. **传统服务器部署**
   - 使用 `scripts/deploy.sh` (Linux/Unix)
   - 使用 `scripts/deploy.ps1` (Windows)
   - 支持systemd服务管理

5. **云服务器部署**
   - 支持腾讯云、阿里云等云平台
   - 提供自动化部署脚本
   - 集成负载均衡和CDN

### 项目状态 ✅

- [x] 基础功能开发完成
- [x] 腾讯云COS集成完成
- [x] 前后端联调测试通过
- [x] 部署配置文件就绪
- [x] 环境检查工具完成
- [ ] 生产环境压力测试
- [ ] 监控和告警配置

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

- **文档**: 查看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) 获取详细部署说明
- **问题**: 提交 GitHub Issue
- **社区**: 加入开发讨论组

---

## 🏠 本地部署 + ☁️ CloudBase 双模式支持

### 🎯 部署模式概览

MemoryDay 项目现在支持 **完整的本地部署** 和 **云端CloudBase部署** 两种模式，可以灵活切换：

#### 1. **本地部署模式** (新增加) ✅
- **本地开发环境** (`local-dev`): Docker容器化开发环境
- **本地生产环境** (`local`): 完整生产环境配置
- **包含服务**: Django后端 + MySQL数据库 + Redis缓存 + Nginx代理

#### 2. **CloudBase部署模式** (原有) ✅  
- **云端环境** (`cloudbase`): 腾讯云CloudBase云函数
- **无需服务器管理**: 自动弹性伸缩，免运维
- **API端点**: `https://whateatday-0gor3cwl4f527bba.tcloudbaseapp.com/api/*`

### 🔄 动态切换功能

小程序支持运行时动态切换部署模式：

```javascript
// 代码切换
const app = getApp()
app.switchDeploymentMode('local')     // 切换到本地部署
app.switchDeploymentMode('cloudbase') // 切换到CloudBase

// 界面切换
进入小程序 → 设置 → 部署配置 → 选择模式
```

### 🚀 快速启动本地部署

#### Windows 系统
```bash
# 一键启动
.\scripts\start-local.ps1

# 或手动启动
docker-compose -f docker-compose.local.yml up -d
```

#### Linux/Mac 系统
```bash
# 一键启动
chmod +x ./scripts/start-local.sh
./scripts/start-local.sh

# 或手动启动
docker-compose -f docker-compose.local.yml up -d
```

### 📊 服务访问地址

| 部署模式 | API地址 | 数据库 | Redis |
|---------|---------|--------|-------|
| 本地开发 | `http://localhost:8000/api` | `localhost:3306` | `localhost:6379` |
| CloudBase | `https://whateatday-0gor3cwl4f527bba.tcloudbaseapp.com/api` | 云端托管 | 云端托管 |

### 🔧 管理命令

```bash
# 查看服务状态
docker-compose -f docker-compose.local.yml ps

# 查看日志
docker-compose -f docker-compose.local.yml logs

# 停止服务
docker-compose -f docker-compose.local.yml down

# 重启服务
docker-compose -f docker-compose.local.yml restart
```

### 📱 小程序配置

在小程序开发工具中配置：
- **服务器域名**: `http://localhost:8000` (本地部署)
- **云开发环境**: `whateatday-0gor3cwl4f527bba` (CloudBase)

### 🎪 部署页面

小程序内置部署配置页面：
- 路径: `/pages/deployment/deployment`
- 功能: 查看当前配置、测试连接、切换模式

### 📚 详细文档

- [本地部署详细指南](LOCAL_DEPLOYMENT_GUIDE.md)
- [CloudBase部署说明](DEPLOYMENT_GUIDE.md)
- [开发环境配置](DEV_GUIDE.md)

## 🎯 下一步计划

1. **性能优化**
   - 图片压缩和CDN加速
   - 数据库查询优化
   - 缓存策略改进

2. **功能扩展**
   - 视频上传支持
   - 多人协作功能
   - 数据分析和推荐

3. **监控运维**
   - 应用性能监控
   - 日志分析和告警
   - 自动化部署流程

---

**项目已成功部署到腾讯云CloudBase！🎉**

**访问地址**: https://whateatday-0gor3cwl4f527bba.tcloudbaseapp.com

**Happy Coding & Deploying! 🚀**