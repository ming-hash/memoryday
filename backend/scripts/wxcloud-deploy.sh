#!/bin/bash
# 微信云托管部署脚本

echo "🚀 开始部署MemoryDay到微信云托管..."

# 检查环境变量
if [ -z "$WX_CLOUD_ENV_ID" ]; then
    echo "❌ 错误: 请设置WX_CLOUD_ENV_ID环境变量"
    exit 1
fi

if [ -z "$WX_CLOUD_APPID" ]; then
    echo "❌ 错误: 请设置WX_CLOUD_APPID环境变量"
    exit 1
fi

# 构建Docker镜像
echo "📦 构建Docker镜像..."
docker build -f Dockerfile.wxcloud -t memoryday-backend:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker构建失败"
    exit 1
fi

# 登录微信云托管
echo "🔐 登录微信云托管..."
tcb login

if [ $? -ne 0 ]; then
    echo "❌ 微信云托管登录失败"
    exit 1
fi

# 部署到云托管
echo "☁️ 部署到微信云托管..."
tcb service:deploy --service memoryday-backend --container memoryday-backend:latest

if [ $? -ne 0 ]; then
    echo "❌ 部署失败"
    exit 1
fi

echo "✅ 部署完成！"
echo ""
echo "📊 部署信息："
echo "   环境ID: $WX_CLOUD_ENV_ID"
echo "   服务名称: memoryday-backend"
echo "   AppID: $WX_CLOUD_APPID"
echo ""
echo "🔗 访问地址："
echo "   云托管服务地址: https://$WX_CLOUD_ENV_ID.service.tcloudbaseapp.com"
echo ""
echo "📝 后续步骤："
echo "   1. 在微信云托管控制台检查服务状态"
echo "   2. 配置小程序调用地址"
echo "   3. 设置环境变量"
echo "   4. 测试服务连通性"