# MemoryDay Django Backend Dockerfile for CloudBase
FROM python:3.9-slim-bullseye

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=memoryday_backend.settings.production
ENV WX_CLOUD=true

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    default-libmysqlclient-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装Python依赖
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 复制后端代码
COPY backend/ .

# 创建必要的目录
RUN mkdir -p /app/logs /app/static /app/media

# 设置权限
RUN groupadd -r django && useradd -r -g django django
RUN chown -R django:django /app
USER django

# 暴露端口（CloudBase云托管默认使用80端口）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# 启动命令
CMD ["gunicorn", "memoryday_backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--access-logfile", "-"]