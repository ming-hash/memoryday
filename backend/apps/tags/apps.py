from django.apps import AppConfig


class TagsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tags'
    verbose_name = '标签管理'
    
    def ready(self):
        # 导入信号处理器
        # import apps.tags.signals  # 暂时注释掉，因为signals模块不存在
        pass