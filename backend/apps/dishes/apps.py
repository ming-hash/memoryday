from django.apps import AppConfig


class DishesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dishes'
    verbose_name = '菜品管理'
    
    def ready(self):
        # 导入信号处理器
        # import apps.dishes.signals  # 暂时注释掉，因为signals模块不存在
        pass