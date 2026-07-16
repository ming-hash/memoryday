"""
Django管理命令：检查COS服务状态
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.cos.services import cos_service


class Command(BaseCommand):
    help = '检查腾讯云COS服务状态'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='显示详细配置信息',
        )
    
    def handle(self, *args, **options):
        verbose = options['verbose']
        
        self.stdout.write('检查腾讯云COS服务状态...')
        self.stdout.write('=' * 50)
        
        # 检查配置
        config = getattr(settings, 'COS_CONFIG', {})
        
        self.stdout.write(f"COS服务启用状态: {'✓ 已启用' if config.get('enabled') else '✗ 未启用'}")
        
        if verbose:
            self.stdout.write('\n配置详情:')
            for key, value in config.items():
                if key in ['secret_key', 'secret_id'] and value:
                    self.stdout.write(f"  {key}: {'*' * 8} (已设置)")
                else:
                    self.stdout.write(f"  {key}: {value}")
        
        # 检查服务可用性
        if cos_service.is_enabled():
            self.stdout.write('\n服务可用性检查:')
            self.stdout.write(f"  客户端状态: {'✓ 正常' if cos_service.client else '✗ 异常'}")
            
            # 测试连接
            try:
                # 尝试列出文件（限制数量为1）
                files = cos_service.list_files(max_keys=1)
                self.stdout.write(f"  连接测试: ✓ 成功 (找到 {len(files)} 个文件)")
            except Exception as e:
                self.stdout.write(f"  连接测试: ✗ 失败 - {str(e)}")
        else:
            self.stdout.write('\n服务不可用，请检查配置')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('检查完成')