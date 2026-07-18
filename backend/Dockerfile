# MemoryDay Django Backend Dockerfile
FROM python:3.9-slim-bullseye

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=memoryday_backend.settings.production

# 使用国内镜像加速 (针对中国服务器)
RUN sed -i 's/deb.debian.org/mirrors.tencent.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.tencent.com/g' /etc/apt/sources.list && \
    pip config set global.index-url https://mirrors.tencent.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.tencent.com

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/static /app/media

# 复制入口脚本
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh

# 创建非root用户
RUN groupadd -r django && useradd -r -g django django
RUN chown -R django:django /app
USER django

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# 启动命令（生产环境使用 gunicorn）
ENTRYPOINT ["/app/docker/entrypoint.sh"]