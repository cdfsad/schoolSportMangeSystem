# ===== Stage 1: builder =====
FROM python:3.11-slim AS builder
WORKDIR /app
# mysqlclient 编译依赖(本项目用 PyMySQL,但保留以兼容)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ===== Stage 2: runtime =====
FROM python:3.11-slim
# 中文项目包名(高校体育场馆管理系统)需 UTF-8 locale
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 10001 appuser
WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY . .
RUN chown -R appuser:appuser /app
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 8000
CMD ["gunicorn", "--config", "gunicorn.conf.py", "高校体育场馆管理系统.wsgi:application"]
