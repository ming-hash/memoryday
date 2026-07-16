#!/usr/bin/env python3
"""
微信云托管环境配置脚本
自动配置云托管所需的环境变量和设置
"""

import os
import json
import argparse
from pathlib import Path

class WXCloudConfigurator:
    def __init__(self, app_id, env_id):
        self.app_id = app_id
        self.env_id = env_id
        self.base_dir = Path(__file__).parent.parent
        
    def generate_wxcloud_config(self):
        """生成微信云托管配置文件"""
        config = {
            "version": "2.0",
            "services": {
                "memoryday-backend": {
                    "service": "memoryday-backend",
                    "provider": {
                        "type": "wx.cloud.container",
                        "version": "1.0"
                    },
                    "framework": {
                        "name": "django",
                        "version": "4.2.7"
                    },
                    "routes": [
                        {
                            "path": "/*",
                            "targetType": "container",
                            "target": "memoryday-backend"
                        }
                    ],
                    "container": {
                        "image": "memoryday-backend:latest",
                        "port": 8000,
                        "cpu": 0.25,
                        "mem": 256,
                        "envVariables": {},
                        "minNum": 1,
                        "maxNum": 3,
                        "policyType": "cpu",
                        "policyThreshold": 80
                    }
                }
            }
        }
        
        # 创建.wxcloud目录
        wxcloud_dir = self.base_dir / ".wxcloud"
        wxcloud_dir.mkdir(exist_ok=True)
        
        # 写入配置文件
        config_file = wxcloud_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print(f"✅ 微信云托管配置文件已生成: {config_file}")
        
    def generate_env_template(self):
        """生成云托管环境变量模板"""
        env_template = """# 微信云托管环境变量配置
# ==================================
# Django配置
DJANGO_SETTINGS_MODULE=memoryday_backend.settings.production
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False

# 微信云托管标识
WX_CLOUD=true
WX_CLOUD_ENV={env_id}
WX_CLOUD_APPID={app_id}

# 数据库配置（云托管推荐使用云数据库）
# 选项1: 使用云数据库
MYSQL_HOST=your-cloud-mysql-host
MYSQL_PORT=3306
MYSQL_DATABASE=memoryday
MYSQL_USER=memoryday_user
MYSQL_PASSWORD=your-mysql-password

# 选项2: 使用微信云数据库（推荐）
# DB_ENV_ID={env_id}

# Redis配置（云托管推荐使用云Redis）
REDIS_URL=redis://your-cloud-redis-host:6379/0

# 微信小程序配置
WECHAT_APPID={app_id}
WECHAT_SECRET=your-wechat-secret

# COS对象存储配置
COS_APP_ID={app_id}
COS_SECRET_ID=your-cos-secret-id
COS_SECRET_KEY=your-cos-secret-key
COS_REGION=ap-beijing
COS_BUCKET=memoryday-1259810697
COS_STORAGE_SUFFIX=1259810697
COS_USE_SIGNED_URL=True

# 其他配置
ALLOWED_HOSTS=*
CORS_ORIGIN_ALLOW_ALL=True
""".format(app_id=self.app_id, env_id=self.env_id)
        
        env_file = self.base_dir / ".env.wxcloud"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)
            
        print(f"✅ 云托管环境变量模板已生成: {env_file}")
        
    def generate_deployment_guide(self):
        """生成部署指南"""
        guide = """# MemoryDay 微信云托管部署指南

## 🚀 快速开始

### 1. 环境准备
- 安装微信云托管CLI: `npm install -g @cloudbase/cli`
- 登录: `tcb login`

### 2. 配置环境变量
将 `.env.wxcloud` 中的配置更新为实际值，然后在云托管控制台设置环境变量。

### 3. 构建镜像
```bash
cd backend
docker build -f Dockerfile.wxcloud -t memoryday-backend:latest .
```

### 4. 部署服务
```bash
# 使用脚本部署
./scripts/wxcloud-deploy.sh

# 或手动部署
tcb service:deploy --service memoryday-backend --container memoryday-backend:latest
```

### 5. 配置小程序调用
在小程序代码中，使用以下方式调用云托管服务：

```javascript
// 云托管调用方式
wx.cloud.callContainer({
  config: {
    env: '{env_id}', // 云托管环境ID
  },
  path: '/api/endpoint', // 服务路径
  method: 'POST',
  data: {{...}},
  success: res => console.log(res),
  fail: err => console.error(err)
})
```

## 🔧 配置说明

### 环境变量优先级
1. 云托管控制台设置的环境变量（最高优先级）
2. .env.wxcloud 文件
3. Dockerfile 中的默认值

### 服务监控
- 健康检查路径: `/api/health/`
- 服务端口: 8000
- 自动扩缩容: CPU使用率 > 80%时扩容

## 📊 优势特性

✅ **免域名备案** - 小程序通过内网直接调用  
✅ **零公网流量** - 前后端走微信内网通信  
✅ **安全防护** - 天然免疫DDoS攻击  
✅ **地域加速** - 就近接入节点，无视后端地域  

## 🛠️ 故障排查

### 服务无法启动
- 检查环境变量是否正确设置
- 查看云托管控制台日志
- 验证Docker镜像构建是否成功

### 小程序调用失败
- 确认环境ID是否正确
- 检查云托管服务状态
- 验证API路径是否正确

## 📞 技术支持

如有问题，请查看：
- 微信云托管官方文档
- 项目README.md
- 项目ISSUE页面
""".format(env_id=self.env_id)
        
        guide_file = self.base_dir / "WXCLOUD_DEPLOYMENT_GUIDE.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
            
        print(f"✅ 部署指南已生成: {guide_file}")

    def setup_complete(self):
        """完成所有配置"""
        print("\n🎉 微信云托管配置完成！")
        print("=" * 50)
        print(f"AppID: {self.app_id}")
        print(f"环境ID: {self.env_id}")
        print("=" * 50)
        print("\n📋 下一步操作：")
        print("1. 更新 .env.wxcloud 中的实际配置")
        print("2. 构建Docker镜像")
        print("3. 部署到微信云托管")
        print("4. 更新小程序调用方式")
        print("\n🔗 详细说明请查看: WXCLOUD_DEPLOYMENT_GUIDE.md")

def main():
    parser = argparse.ArgumentParser(description='微信云托管配置工具')
    parser.add_argument('--appid', required=True, help='微信小程序AppID')
    parser.add_argument('--env', required=True, help='云托管环境ID')
    
    args = parser.parse_args()
    
    configurator = WXCloudConfigurator(args.appid, args.env)
    
    print("🔧 开始配置微信云托管环境...")
    
    # 生成配置文件
    configurator.generate_wxcloud_config()
    configurator.generate_env_template()
    configurator.generate_deployment_guide()
    
    # 完成配置
    configurator.setup_complete()

if __name__ == "__main__":
    main()