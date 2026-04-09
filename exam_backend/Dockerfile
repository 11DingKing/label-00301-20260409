# ============================================
# Django Backend Dockerfile
# 支持 ARM64 (Apple Silicon/M1/M2) 和 AMD64 (x86_64)
# ============================================

# 构建阶段
FROM --platform=$BUILDPLATFORM python:3.11-slim AS builder

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# 生产阶段
# ============================================
FROM python:3.11-slim AS production

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 复制项目文件
COPY --chown=appuser:appuser . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 收集静态文件
RUN python manage.py collectstatic --noinput --settings=config.settings.prod || true

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/docs/ || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "config.wsgi:application"]
