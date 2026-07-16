from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = '用户管理'
    
    def ready(self):
        # 导入信号处理器
        # import apps.users.signals  # 暂时注释掉，因为signals模块不存在
        pass