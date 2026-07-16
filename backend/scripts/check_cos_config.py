#!/usr/bin/env python
"""
COS配置检查脚本
检查腾讯云COS配置是否正确
"""
import os
import sys
import django

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memoryday_backend.settings')
django.setup()

from django.conf import settings
from apps.cos.services import cos_service


def check_cos_config():
    """检查COS配置"""
    print("=" * 60)
    print("腾讯云COS配置检查")
    print("=" * 60)
    
    # 检查配置是否存在
    config = getattr(settings, 'COS_CONFIG', {})
    if not config:
        print("❌ 未找到COS配置")
        return False
    
    print(f"✅ 找到COS配置，共{len(config)}个配置项")
    
    # 检查关键配置项
    required_keys = ['enabled', 'secret_id', 'secret_key', 'bucket', 'region']
    missing_keys = []
    
    for key in required_keys:
        if key not in config:
            missing_keys.append(key)
        else:
            value = config[key]
            if key in ['secret_id', 'secret_key']:
                display_value = '***' if value else '未设置'
            else:
                display_value = value
            print(f"   {key}: {display_value}")
    
    if missing_keys:
        print(f"❌ 缺少关键配置项: {', '.join(missing_keys)}")
        return False
    
    # 检查配置值
    if not config.get('enabled'):
        print("⚠️  COS服务未启用")
        return True
    
    if not config.get('secret_id') or not config.get('secret_key'):
        print("❌ SecretId或SecretKey未设置")
        return False
    
    if not config.get('bucket'):
        print("❌ Bucket名称未设置")
        return False
    
    # 检查服务可用性
    print("\n🔧 检查服务可用性...")
    
    if not cos_service.is_enabled():
        print("❌ COS服务不可用")
        return False
    
    print("✅ COS服务已启用")
    
    # 测试连接
    try:
        files = cos_service.list_files(max_keys=1)
        print(f"✅ 连接测试成功 (找到 {len(files)} 个文件)")
    except Exception as e:
        print(f"❌ 连接测试失败: {str(e)}")
        return False
    
    print("\n🎉 COS配置检查完成！")
    return True


def main():
    """主函数"""
    try:
        success = check_cos_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 检查过程中发生错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()