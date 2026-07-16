# MemoryDay 本地部署指南

## 🏠 本地部署概述

MemoryDay 项目支持完整的本地部署方案，包含后端API服务、MySQL数据库、Redis缓存等全套服务。通过Docker容器化部署，可以快速在本地电脑上搭建完整的开发和生产环境。

### 🎯 部署模式

1. **本地开发环境** (`local-dev`)
   - 使用Docker容器运行后端服务
   - 支持热重载开发
   - 适合开发和调试

2. **本地生产环境** (`local`)
   - 完整生产环境配置
   - 包含Nginx反向代理
   - 支持SSL证书

3. **云端部署** (`cloudbase`)
   - 腾讯云CloudBase云函数
   - 无需管理服务器
   - 自动弹性伸缩

## 🚀 快速开始

### 环境要求

- **Docker** 20.10+ 和 **Docker Compose** 1.29+
- 至少 4GB 可用内存
- 至少 2GB 可用磁盘空间

### 一键启动

#### Windows 系统
```bash
# 使用PowerShell脚本
.\scripts\start-local.ps1

# 或使用Docker Compose直接启动
docker-compose -f docker-compose.local.yml up -d
```

#### Linux/Mac 系统
```bash
# 使用Shell脚本
chmod +x ./scripts/start-local.sh
./scripts/start-local.sh

# 或使用Docker Compose直接启动
docker-compose -f docker-compose.local.yml up -d
```

### 环境配置

1. **复制环境配置文件**
   ```bash
   cp .env.local.example .env.local
   ```

2. **编辑配置文件** (可选)
   ```bash
   # 编辑 .env.local 文件
   # 修改数据库密码等配置
   MYSQL_ROOT_PASSWORD=your-secure-password
   MYSQL_PASSWORD=your-app-password
   ```

## 🔧 服务说明

### 启动的服务

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端API | 8000 | Django REST API服务 |
| MySQL数据库 | 3306 | 应用数据库 |
| Redis缓存 | 6379 | 缓存和会话存储 |

### 服务访问地址

- **后端API**: http://localhost:8000/api
- **健康检查**: http://localhost:8000/api/health/
- **数据库**: localhost:3306 (用户: memoryday_user)
- **Redis**: localhost:6379

## 📱 小程序配置

### 开发环境配置

在小程序开发工具中配置服务器域名：

1. 打开微信开发者工具
2. 进入项目设置 → 开发设置
3. 添加服务器域名：
   - **request合法域名**: `http://localhost:8000`
   - **uploadFile合法域名**: `http://localhost:8000`
   - **downloadFile合法域名**: `http://localhost:8000`

### 部署模式切换

小程序支持动态切换部署模式：

1. **通过代码切换**
   ```javascript
   const app = getApp()
   
   // 切换到本地部署
   app.globalData.deploymentMode = 'local'
   app.globalData.baseUrl = 'http://localhost:8000/api'
   app.globalData.useCloudBase = false
   
   // 切换到CloudBase
   app.globalData.deploymentMode = 'cloudbase'
   app.globalData.baseUrl = 'https://whateatday-0gor3cwl4f527bba.tcloudbaseapp.com/api'
   app.globalData.useCloudBase = true
   ```

2. **通过界面切换**
   - 进入小程序 → 设置 → 部署配置
   - 选择需要的部署模式
   - 重启小程序生效

## 🔄 管理命令

### 常用命令

```bash
# 启动服务
docker-compose -f docker-compose.local.yml up -d

# 停止服务
docker-compose -f docker-compose.local.yml down

# 查看日志
docker-compose -f docker-compose.local.yml logs

# 重启服务
docker-compose -f docker-compose.local.yml restart

# 查看服务状态
docker-compose -f docker-compose.local.yml ps
```

### 数据库管理

```bash
# 进入数据库容器
docker exec -it memoryday-db-dev mysql -u memoryday_user -p

# 备份数据库
docker exec memoryday-db-dev mysqldump -u memoryday_user -p memoryday > backup.sql

# 恢复数据库
docker exec -i memoryday-db-dev mysql -u memoryday_user -p memoryday < backup.sql
```

## 🛠️ 开发调试

### 热重载开发

对于后端代码修改，可以使用热重载模式：

```bash
# 进入后端容器
docker exec -it memoryday-backend-dev bash

# 在容器内启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 数据库迁移

```bash
# 进入后端容器
docker exec -it memoryday-backend-dev bash

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

## 🐛 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -ano | findstr :8000  # Windows
   lsof -i :8000                 # Linux/Mac
   ```

2. **容器启动失败**
   ```bash
   # 查看详细日志
   docker-compose -f docker-compose.local.yml logs backend
   
   # 重新构建镜像
   docker-compose -f docker-compose.local.yml build --no-cache
   ```

3. **数据库连接失败**
   ```bash
   # 检查数据库状态
   docker-compose -f docker-compose.local.yml logs db
   
   # 重启数据库服务
   docker-compose -f docker-compose.local.yml restart db
   ```

### 性能优化

1. **调整资源限制**
   ```yaml
   # 在docker-compose.local.yml中调整
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 1G
             cpus: '1.0'
   ```

2. **启用缓存优化**
   ```bash
   # 配置Redis缓存
   docker-compose -f docker-compose.local.yml up -d redis
   ```

## 📚 进阶配置

### 生产环境部署

对于生产环境部署，使用完整配置：

```bash
# 使用生产环境配置
docker-compose up -d

# 包含Nginx反向代理和SSL
docker-compose -f docker-compose.yml up -d nginx
```

### 监控和日志

```bash
# 查看实时日志
docker-compose -f docker-compose.local.yml logs -f

# 监控服务状态
docker stats

# 查看容器资源使用
docker container stats
```

## 🤝 贡献指南

欢迎贡献本地部署相关的改进：

1. 提交Issue报告问题
2. 提交Pull Request提供改进
3. 更新部署文档

## 📞 技术支持

如果遇到部署问题：

1. 查看本指南的故障排除部分
2. 检查项目Issue列表
3. 提交新的Issue描述问题

---

**Happy Coding! 🎉**