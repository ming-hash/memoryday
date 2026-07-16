from django.apps import AppConfig


class StatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.stats'
    verbose_name = '统计分析'
    
    def ready(self):
        # 导入信号处理器
        # import apps.stats.signals  # 暂时注释掉，因为signals模块不存在
        pass