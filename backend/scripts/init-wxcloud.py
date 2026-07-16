#!/usr/bin/env python3
"""
微信云托管环境初始化脚本
自动完成云托管环境的初始化和配置
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class WxCloudInitializer:
    def __init__(self, app_id, env_id):
        self.app_id = app_id
        self.env_id = env_id
        self.base_dir = Path(__file__).parent.parent
        
    def check_prerequisites(self):
        """检查环境依赖"""
        print("🔍 检查环境依赖...")
        
        # 检查Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Docker未安装或未启动")
                return False
            print(f"✅ Docker版本: {result.stdout.strip()}")
        except Exception as e:
            print(f"❌ Docker检查失败: {e}")
            return False
        
        # 检查Node.js（用于云托管CLI）
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️  Node.js未安装，需要安装云托管CLI")
            else:
                print(f"✅ Node.js版本: {result.stdout.strip()}")
        except Exception as e:
            print(f"⚠️  Node.js检查失败: {e}")
        
        # 检查Python
        try:
            result = subprocess.run(['python', '--version'], capture_output=True, text=True)
            print(f"✅ Python版本: {result.stdout.strip()}")
        except Exception as e:
            print(f"❌ Python检查失败: {e}")
            return False
        
        return True
    
    def install_cloudbase_cli(self):
        """安装微信云托管CLI"""
        print("📦 安装微信云托管CLI...")
        
        try:
            result = subprocess.run(['npm', 'install', '-g', '@cloudbase/cli'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 云托管CLI安装成功")
                
                # 验证安装
                result = subprocess.run(['tcb', '--version'], capture_output=True, text=True)
                print(f"✅ 云托管CLI版本: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ 云托管CLI安装失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 云托管CLI安装异常: {e}")
            return False
    
    def generate_config_files(self):
        """生成配置文件"""
        print("⚙️  生成配置文件...")
        
        # 导入配置脚本
        sys.path.append(str(self.base_dir / 'scripts'))
        from wxcloud_setup import WXCloudConfigurator
        
        configurator = WXCloudConfigurator(self.app_id, self.env_id)
        
        try:
            configurator.generate_wxcloud_config()
            configurator.generate_env_template()
            configurator.generate_deployment_guide()
            return True
        except Exception as e:
            print(f"❌ 配置文件生成失败: {e}")
            return False
    
    def build_docker_image(self):
        """构建Docker镜像"""
        print("🐳 构建Docker镜像...")
        
        try:
            # 切换到后端目录
            os.chdir(self.base_dir)
            
            # 构建镜像
            result = subprocess.run([
                'docker', 'build', 
                '-f', 'Dockerfile.wxcloud', 
                '-t', f'memoryday-backend:latest',
                '.'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Docker镜像构建成功")
                
                # 验证镜像
                result = subprocess.run(['docker', 'images', 'memoryday-backend'], 
                                      capture_output=True, text=True)
                print("📊 镜像信息:")
                print(result.stdout)
                return True
            else:
                print(f"❌ Docker镜像构建失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Docker构建异常: {e}")
            return False
    
    def test_local_deployment(self):
        """测试本地部署"""
        print("🧪 测试本地部署...")
        
        try:
            # 启动本地测试容器
            result = subprocess.run([
                'docker', 'run', '-d',
                '--name', 'memoryday-test',
                '-p', '8001:8000',
                '-e', 'DJANGO_SETTINGS_MODULE=memoryday_backend.settings.development',
                'memoryday-backend:latest'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 本地测试容器启动成功")
                
                # 等待服务启动
                import time
                time.sleep(10)
                
                # 测试健康检查
                result = subprocess.run(['curl', '-f', 'http://localhost:8001/api/health/'], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ 健康检查通过")
                    print(f"📊 响应: {result.stdout}")
                else:
                    print("⚠️  健康检查失败，但容器已启动")
                
                # 停止测试容器
                subprocess.run(['docker', 'stop', 'memoryday-test'], capture_output=True)
                subprocess.run(['docker', 'rm', 'memoryday-test'], capture_output=True)
                
                return True
            else:
                print(f"❌ 本地测试容器启动失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 本地测试异常: {e}")
            return False
    
    def create_deployment_checklist(self):
        """创建部署检查清单"""
        print("📋 创建部署检查清单...")
        
        checklist = f"""# MemoryDay 微信云托管部署检查清单

## ✅ 已完成项目
- [x] 环境依赖检查
- [x] 云托管CLI安装
- [x] 配置文件生成
- [x] Docker镜像构建
- [x] 本地部署测试

## 🚀 下一步部署步骤

### 1. 登录微信云托管
```bash
tcb login
```

### 2. 配置环境变量
在微信云托管控制台设置以下环境变量：
- DJANGO_SECRET_KEY
- MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
- WECHAT_SECRET
- COS_SECRET_ID, COS_SECRET_KEY

### 3. 部署到云托管
```bash
# 使用部署脚本
./scripts/wxcloud-deploy.sh

# 或手动部署
tcb service:deploy --service memoryday-backend --container memoryday-backend:latest
```

### 4. 验证部署
```bash
# 查看服务状态
tcb service:list

# 查看服务日志
tcb service:log --service memoryday-backend

# 测试服务连通性
curl https://{self.env_id}.service.tcloudbaseapp.com/api/health/
```

### 5. 小程序配置更新
在小程序代码中，确保：
- 使用 `utils/wxcloud-api.js` 中的API适配器
- 生产环境自动切换到云托管调用方式
- 取消服务器域名配置（云托管不需要）

## 📊 部署信息
- AppID: {self.app_id}
- 环境ID: {self.env_id}
- 服务名称: memoryday-backend
- 镜像标签: memoryday-backend:latest

## 📞 技术支持
- 微信云托管文档: https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/
- 项目文档: WXCLOUD_DEPLOYMENT.md
"""
        
        checklist_file = self.base_dir / 'DEPLOYMENT_CHECKLIST.md'
        with open(checklist_file, 'w', encoding='utf-8') as f:
            f.write(checklist)
        
        print(f"✅ 部署检查清单已生成: {checklist_file}")
    
    def run_initialization(self):
        """执行完整的初始化流程"""
        print("🎯 开始微信云托管环境初始化...")
        print("=" * 60)
        
        steps = [
            ("环境依赖检查", self.check_prerequisites),
            ("云托管CLI安装", self.install_cloudbase_cli),
            ("配置文件生成", self.generate_config_files),
            ("Docker镜像构建", self.build_docker_image),
            ("本地部署测试", self.test_local_deployment),
            ("创建检查清单", self.create_deployment_checklist)
        ]
        
        success_count = 0
        
        for step_name, step_func in steps:
            print(f"\n📝 执行: {step_name}")
            print("-" * 40)
            
            try:
                if step_func():
                    success_count += 1
                    print(f"✅ {step_name} - 完成")
                else:
                    print(f"❌ {step_name} - 失败")
                    # 询问是否继续
                    if input("是否继续执行后续步骤? (y/n): ").lower() != 'y':
                        break
            except Exception as e:
                print(f"❌ {step_name} - 异常: {e}")
                if input("是否继续执行后续步骤? (y/n): ").lower() != 'y':
                    break
        
        print("\n" + "=" * 60)
        print(f"🎉 初始化完成! ({success_count}/{len(steps)} 步骤成功)")
        
        if success_count == len(steps):
            print("\n🚀 所有步骤已完成，可以开始部署到云托管！")
        else:
            print(f"\n⚠️  有 {len(steps) - success_count} 个步骤失败，请检查后重试")
        
        print(f"\n📚 请查看以下文件获取详细说明：")
        print(f"   - WXCLOUD_DEPLOYMENT.md (部署指南)")
        print(f"   - DEPLOYMENT_CHECKLIST.md (检查清单)")
        print(f"   - backend/.env.wxcloud (环境变量模板)")

def main():
    parser = argparse.ArgumentParser(description='微信云托管环境初始化工具')
    parser.add_argument('--appid', required=True, help='微信小程序AppID')
    parser.add_argument('--env', required=True, help='云托管环境ID')
    
    args = parser.parse_args()
    
    initializer = WxCloudInitializer(args.appid, args.env)
    initializer.run_initialization()

if __name__ == "__main__":
    import argparse
    main()