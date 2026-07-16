#!/usr/bin/env python3
"""
MemoryDay 后端项目安装脚本
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令行命令"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"命令执行失败: {cmd}")
            print(f"错误输出: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return False

def main():
    """主安装函数"""
    print("🚀 开始设置 MemoryDay 后端项目...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        sys.exit(1)
    
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # 创建虚拟环境
    venv_dir = backend_dir / ".venv"
    if not venv_dir.exists():
        print("📦 创建虚拟环境...")
        venv.create(venv_dir, with_pip=True)
    
    # 确定pip路径
    pip_path = venv_dir / "Scripts" / "pip.exe" if os.name == "nt" else venv_dir / "bin" / "pip"
    python_path = venv_dir / "Scripts" / "python.exe" if os.name == "nt" else venv_dir / "bin" / "python"
    
    if not pip_path.exists():
        print("❌ 虚拟环境创建失败")
        sys.exit(1)
    
    # 安装依赖
    print("📦 安装依赖包...")
    if not run_command(f'"{pip_path}" install -r requirements.txt'):
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    # 创建数据库迁移
    print("🗄️ 创建数据库迁移...")
    if not run_command(f'"{python_path}" manage.py makemigrations'):
        print("⚠️ 迁移创建失败，可能是首次运行")
    
    # 应用数据库迁移
    print("🗄️ 应用数据库迁移...")
    if not run_command(f'"{python_path}" manage.py migrate'):
        print("❌ 迁移应用失败")
        sys.exit(1)
    
    # 创建超级用户（可选）
    print("👤 创建超级用户（按Ctrl+C跳过）...")
    try:
        run_command(f'"{python_path}" manage.py createsuperuser', timeout=30)
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        print("⏭️ 跳过创建超级用户")
    
    print("✅ 设置完成！")
    print("\n🎯 接下来可以：")
    print("1. 启动开发服务器: python manage.py runserver")
    print("2. 访问管理后台: http://127.0.0.1:8000/admin")
    print("3. 查看API文档: http://127.0.0.1:8000/swagger/")

if __name__ == "__main__":
    main()