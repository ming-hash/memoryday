# MemoryDay 微信云托管部署指南

## 🎯 为什么选择微信云托管？

### ✅ 核心优势
- **免域名备案** - 小程序通过内网直接调用，无需购买和备案域名
- **零公网流量** - 前后端走微信内网通信，不产生额外流量费用
- **安全防护** - 天然免疫DDoS攻击，仅授权小程序可访问
- **地域加速** - 就近接入节点，无视后端地域影响
- **自动扩缩容** - 根据CPU使用率自动调整实例数量

## 📋 部署前准备

### 1. 环境要求
- 微信小程序 AppID: `wxbe5cb0f551d030e5`
- 微信云托管环境（需要申请）
- Docker 环境
- Node.js 环境（用于云托管CLI）

### 2. 安装云托管CLI
```bash
# 安装微信云托管CLI
npm install -g @cloudbase/cli

# 登录云托管
tcb login
```

## 🚀 快速部署流程

### 步骤1：配置环境变量

```bash
# 进入项目后端目录
cd backend

# 运行配置脚本（生成云托管配置文件）
python scripts/wxcloud-setup.py --appid wxbe5cb0f551d030e5 --env your-env-id
```

### 步骤2：更新环境变量文件
编辑 `backend/.env.wxcloud`，更新以下关键配置：

```ini
# Django安全配置
DJANGO_SECRET_KEY=your-generated-secret-key-here

# 数据库配置（推荐使用云数据库）
MYSQL_HOST=your-cloud-mysql-host
MYSQL_DATABASE=memoryday
MYSQL_USER=memoryday_user
MYSQL_PASSWORD=your-mysql-password

# 微信小程序配置
WECHAT_SECRET=your-wechat-secret

# COS配置
COS_SECRET_ID=your-cos-secret-id
COS_SECRET_KEY=your-cos-secret-key
```

### 步骤3：构建Docker镜像

```bash
# 使用云托管优化版Dockerfile构建镜像
docker build -f Dockerfile.wxcloud -t memoryday-backend:latest .

# 验证镜像构建
docker images | grep memoryday-backend
```

### 步骤4：部署到云托管

#### 方式一：使用自动部署脚本
```bash
# 设置环境变量
export WX_CLOUD_ENV_ID=your-env-id
export WX_CLOUD_APPID=wxbe5cb0f551d030e5

# 执行部署脚本
./scripts/wxcloud-deploy.sh
```

#### 方式二：手动部署
```bash
# 登录云托管
tcb login

# 部署服务
tcb service:deploy --service memoryday-backend --container memoryday-backend:latest
```

## 🔧 小程序端配置

### 1. 更新API调用方式

生产环境会自动使用云托管调用方式：

```javascript
// 传统方式（开发环境）
wx.request({
  url: 'http://localhost:8000/api/dishes',
  method: 'GET',
  success: res => console.log(res)
})

// 云托管方式（生产环境，自动切换）
wx.cloud.callContainer({
  config: {
    env: 'prod-memoryday',
    service: 'memoryday-backend'
  },
  path: '/api/dishes',
  method: 'GET',
  success: res => console.log(res)
})
```

### 2. 环境检测逻辑

小程序会自动检测环境并选择正确的调用方式：

```javascript
// 在 app.js 中自动配置
onLaunch() {
  if (isDevelopment()) {
    // 开发环境：使用传统API
    this.globalData.baseUrl = 'http://localhost:8000/api'
    this.globalData.useWxCloud = false
  } else {
    // 生产环境：使用云托管
    this.globalData.baseUrl = ''
    this.globalData.useWxCloud = true
    this.globalData.wxCloudEnv = 'prod-memoryday'
  }
}
```

## 📊 服务监控与管理

### 1. 服务状态监控

- **健康检查路径**: `/api/health/`
- **服务端口**: 8000
- **自动扩缩容**: CPU使用率 > 80%时自动扩容

### 2. 日志查看

```bash
# 查看服务日志
tcb service:log --service memoryday-backend

# 实时查看日志
tcb service:log --service memoryday-backend --tail
```

### 3. 服务管理

```bash
# 查看服务列表
tcb service:list

# 查看服务详情
tcb service:detail --service memoryday-backend

# 重启服务
tcb service:restart --service memoryday-backend
```

## 🛠️ 数据库配置建议

### 选项1：使用微信云数据库（推荐）

```ini
# 在 .env.wxcloud 中配置
DB_ENV_ID=your-env-id
```

### 选项2：使用外部云数据库

```ini
# 在云托管控制台设置环境变量
MYSQL_HOST=your-mysql-host.com
MYSQL_PORT=3306
MYSQL_DATABASE=memoryday
MYSQL_USER=memoryday_user
MYSQL_PASSWORD=your-password
```

## 🔒 安全配置

### 1. 环境变量安全
- 敏感信息（如数据库密码、微信密钥）必须在云托管控制台设置
- 不要将敏感信息提交到代码仓库

### 2. 网络访问控制
- 建议关闭公网访问，仅允许小程序内网调用
- 配置IP白名单（如需要外部访问）

### 3. 数据加密
- 数据库连接使用SSL
- 敏感数据传输使用HTTPS

## 🚨 故障排查

### 常见问题

#### 问题1：服务无法启动
```bash
# 检查环境变量
tcb service:env --service memoryday-backend

# 查看详细日志
tcb service:log --service memoryday-backend --lines 100
```

#### 问题2：小程序调用失败
```javascript
// 检查环境配置
console.log('云托管环境:', app.globalData.wxCloudEnv)
console.log('使用云托管:', app.globalData.useWxCloud)

// 检查网络权限
wx.getNetworkType({
  success: res => console.log('网络类型:', res.networkType)
})
```

#### 问题3：数据库连接失败
```bash
# 检查数据库连接信息
echo $MYSQL_HOST
echo $MYSQL_PORT

# 测试数据库连接
mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE
```

### 调试工具

```bash
# 进入容器调试
tcb service:exec --service memoryday-backend --command "/bin/bash"

# 检查服务状态
curl http://localhost:8000/api/health/
```

## 📈 性能优化建议

### 1. 资源配置
- **CPU**: 0.25核（起步）→ 0.5核（生产）
- **内存**: 256MB（起步）→ 512MB（生产）
- **实例数**: 1-3个（根据负载自动调整）

### 2. 缓存策略
- 使用Redis缓存频繁访问的数据
- 配置合理的缓存过期时间
- 使用CDN加速静态资源

### 3. 数据库优化
- 添加合适的索引
- 使用连接池
- 定期清理过期数据

## 🔄 持续集成/持续部署

### GitHub Actions 示例

```yaml
name: Deploy to WX Cloud
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
    
    - name: Install CloudBase CLI
      run: npm install -g @cloudbase/cli
    
    - name: Build Docker Image
      run: docker build -f backend/Dockerfile.wxcloud -t memoryday-backend:latest .
    
    - name: Deploy to WX Cloud
      run: |
        tcb login --apiKeyId ${{ secrets.WX_CLOUD_API_KEY_ID }} --apiKey ${{ secrets.WX_CLOUD_API_KEY }}
        tcb service:deploy --service memoryday-backend --container memoryday-backend:latest
```

## 📞 技术支持

- **微信云托管文档**: https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/
- **项目文档**: 查看 `README.md`
- **问题反馈**: 创建 GitHub Issue

## 🎉 部署完成检查清单

- [ ] 云托管环境已创建
- [ ] Docker镜像构建成功
- [ ] 环境变量配置正确
- [ ] 服务部署成功
- [ ] 健康检查通过
- [ ] 小程序调用测试通过
- [ ] 数据库连接正常
- [ ] 文件上传功能正常

---

**注意**: 部署完成后，请在小程序后台取消服务器域名配置，因为云托管服务不需要域名即可调用。