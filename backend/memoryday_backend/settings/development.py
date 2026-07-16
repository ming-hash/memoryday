"""
开发环境设置
"""

from .base import *

# 数据库配置 - 开发环境使用SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 允许所有主机在开发环境
ALLOWED_HOSTS = ['*']

# CORS设置 - 开发环境允许所有来源
CORS_ALLOW_ALL_ORIGINS = True

# COS配置 - 直接从环境变量读取（不覆盖base.py的配置）
# 注意：COS_SECRET_ID 和 COS_SECRET_KEY 在 .env 文件中定义

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}