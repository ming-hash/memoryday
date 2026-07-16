#!/bin/bash

# MemoryDay 本地部署启动脚本

echo "🚀 启动 MemoryDay 本地部署环境..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误：Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查环境变量文件
if [ ! -f ".env.local" ]; then
    echo "📝 创建本地环境配置文件..."
    cp .env.local.example .env.local
    echo "⚠️  请编辑 .env.local 文件配置数据库密码等参数"
fi

# 加载环境变量
if [ -f ".env.local" ]; then
    echo "📋 加载本地环境配置..."
    source .env.local
fi

echo "🔧 检查Docker服务状态..."
docker-compose -f docker-compose.local.yml up -d

echo "⏳ 等待服务启动..."
sleep 10

echo "🔍 检查服务状态..."
# 检查后端服务
if curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
    echo "✅ 后端API服务运行正常"
else
    echo "❌ 后端API服务启动失败，请检查日志"
    docker-compose -f docker-compose.local.yml logs backend
fi

# 检查数据库服务
if docker exec memoryday-db-dev mysql -u memoryday_user -pmemoryday_password -e "SELECT 1;" memoryday > /dev/null 2>&1; then
    echo "✅ 数据库服务运行正常"
else
    echo "❌ 数据库服务启动失败，请检查日志"
    docker-compose -f docker-compose.local.yml logs db
fi

echo ""
echo "🎉 MemoryDay 本地部署环境已启动完成！"
echo ""
echo "📊 服务访问地址："
echo "   - 后端API：http://localhost:8000/api"
echo "   - 数据库：localhost:3306 (用户: memoryday_user)"
echo "   - Redis：localhost:6379"
echo ""
echo "📝 管理命令："
echo "   - 查看日志：docker-compose -f docker-compose.local.yml logs"
echo "   - 停止服务：docker-compose -f docker-compose.local.yml down"
echo "   - 重启服务：docker-compose -f docker-compose.local.yml restart"
echo ""
echo "💡 提示：小程序开发工具中，请将服务器域名设置为：http://localhost:8000"