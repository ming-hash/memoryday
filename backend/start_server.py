#!/usr/bin/env python3
"""
MemoryDay 开发服务器启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def run_server():
    """启动开发服务器"""
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # 检查虚拟环境
    venv_dir = backend_dir / ".venv"
    python_path = venv_dir / "Scripts" / "python.exe" if os.name == "nt" else venv_dir / "bin" / "python"
    
    if not venv_dir.exists() or not python_path.exists():
        print("❌ 虚拟环境未找到，请先运行 setup.py")
        sys.exit(1)
    
    print("🚀 启动 MemoryDay 开发服务器...")
    print("📍 访问地址: http://127.0.0.1:8000")
    print("📚 API文档: http://127.0.0.1:8000/swagger/")
    print("🔧 管理后台: http://127.0.0.1:8000/admin/")
    print("⏹️ 按 Ctrl+C 停止服务器\n")
    
    try:
        # 启动Django开发服务器
        subprocess.run([str(python_path), "manage.py", "runserver"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()