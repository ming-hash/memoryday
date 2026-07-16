#!/usr/bin/env python3
"""
MemoryDay Quick Configuration Check Tool
A lightweight script for quick environment validation.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = project_root / '.env'
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env and configure it")
        return False
    
    # Read and check key variables
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_vars = [
        'DJANGO_SECRET_KEY',
        'MYSQL_DATABASE',
        'MYSQL_USER', 
        'MYSQL_PASSWORD',
        'MYSQL_HOST'
    ]
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in content or f"{var}=your-" in content:
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ .env file has missing or default values for:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ .env file is properly configured")
    return True


def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'django',
        'djangorestframework', 
        'mysqlclient',
        'redis',
        'qcloud-cos-python',
        'django-environ'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing Python packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All Python dependencies are installed")
    return True


def check_directory_structure():
    """Check if project directory structure is correct"""
    required_dirs = [
        'apps',
        'apps/cos',
        'apps/users', 
        'apps/dishes',
        'memoryday_backend',
        'logs',
        'static',
        'media'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        return False
    
    print("✅ Project directory structure is correct")
    return True


def check_cos_config():
    """Quick check for COS configuration"""
    try:
        # Try to import COS service
        from apps.cos.services import COSService
        
        # Check if COS is enabled in environment
        cos_enabled = os.getenv('COS_ENABLED', 'False').lower() == 'true'
        
        if cos_enabled:
            required_cos_vars = ['COS_SECRET_ID', 'COS_SECRET_KEY', 'COS_BUCKET', 'COS_REGION']
            missing_cos_vars = []
            
            for var in required_cos_vars:
                if not os.getenv(var):
                    missing_cos_vars.append(var)
            
            if missing_cos_vars:
                print("⚠️ COS enabled but missing variables:")
                for var in missing_cos_vars:
                    print(f"   - {var}")
                return False
            else:
                print("✅ COS configuration looks good")
                return True
        else:
            print("ℹ️  COS is disabled (set COS_ENABLED=True to enable)")
            return True
            
    except ImportError as e:
        print("❌ COS service module not found")
        return False


def main():
    """Run all quick checks"""
    print("🔍 Running MemoryDay Quick Configuration Check...")
    print("=" * 50)
    
    checks = [
        ("Environment File", check_env_file),
        ("Python Dependencies", check_python_dependencies), 
        ("Directory Structure", check_directory_structure),
        ("COS Configuration", check_cos_config)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\nChecking {check_name}...")
        result = check_func()
        results.append((check_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 QUICK CHECK SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! You're ready to run the application.")
        print("\nNext steps:")
        print("1. Run database migrations: python manage.py migrate")
        print("2. Start the server: python manage.py runserver")
        print("3. Test COS configuration: python manage.py cos_status")
    else:
        print("\n💡 Fix the issues above before running the application.")
        sys.exit(1)


if __name__ == "__main__":
    main()