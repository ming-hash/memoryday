# MemoryDay 本地部署启动脚本 (PowerShell)

Write-Host "🚀 启动 MemoryDay 本地部署环境..." -ForegroundColor Green

# 检查Docker是否安装
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 错误：Docker 未安装，请先安装 Docker" -ForegroundColor Red
    exit 1
}

if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 错误：Docker Compose 未安装，请先安装 Docker Compose" -ForegroundColor Red
    exit 1
}

# 检查环境变量文件
if (!(Test-Path ".env.local")) {
    Write-Host "📝 创建本地环境配置文件..." -ForegroundColor Yellow
    Copy-Item ".env.local.example" ".env.local" -ErrorAction SilentlyContinue
    Write-Host "⚠️  请编辑 .env.local 文件配置数据库密码等参数" -ForegroundColor Yellow
}

Write-Host "🔧 启动Docker服务..." -ForegroundColor Cyan
docker-compose -f docker-compose.local.yml up -d

Write-Host "⏳ 等待服务启动..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "🔍 检查服务状态..." -ForegroundColor Cyan

# 检查后端服务
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -TimeoutSec 10
    Write-Host "✅ 后端API服务运行正常" -ForegroundColor Green
} catch {
    Write-Host "❌ 后端API服务启动失败，请检查日志" -ForegroundColor Red
    docker-compose -f docker-compose.local.yml logs backend
}

# 检查数据库服务
try {
    docker exec memoryday-db-dev mysql -u memoryday_user -pmemoryday_password -e "SELECT 1;" memoryday 2>&1 | Out-Null
    Write-Host "✅ 数据库服务运行正常" -ForegroundColor Green
} catch {
    Write-Host "❌ 数据库服务启动失败，请检查日志" -ForegroundColor Red
    docker-compose -f docker-compose.local.yml logs db
}

Write-Host ""
Write-Host "🎉 MemoryDay 本地部署环境已启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📊 服务访问地址：" -ForegroundColor Cyan
Write-Host "   - 后端API：http://localhost:8000/api"
Write-Host "   - 数据库：localhost:3306 (用户: memoryday_user)"
Write-Host "   - Redis：localhost:6379"
Write-Host ""
Write-Host "📝 管理命令：" -ForegroundColor Cyan
Write-Host "   - 查看日志：docker-compose -f docker-compose.local.yml logs"
Write-Host "   - 停止服务：docker-compose -f docker-compose.local.yml down"
Write-Host "   - 重启服务：docker-compose -f docker-compose.local.yml restart"
Write-Host ""
Write-Host "💡 提示：小程序开发工具中，请将服务器域名设置为：http://localhost:8000" -ForegroundColor Yellow