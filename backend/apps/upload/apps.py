from django.apps import AppConfig


class UploadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.upload'
    verbose_name = '文件上传'
    
    def ready(self):
        # 导入信号处理器
        # import apps.upload.signals  # 暂时注释掉，因为signals模块不存在
        pass