from django.apps import AppConfig


class CosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cos'
    verbose_name = '腾讯云COS集成'