"""
Gunicorn 生产 WSGI 启动配置。

用法(在容器/服务器中):
    gunicorn -c gunicorn.conf.py 高校体育场馆管理系统.wsgi:application

说明:
- bind / workers / timeout 适合中小流量校园系统;
- 关键参数从环境变量读取,便于容器化部署;
- 使用 sync worker(本系统 P0/P1 阶段为纯同步,Django ORM + MySQL)。
"""
import multiprocessing
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 60))
graceful_timeout = 30
keepalive = 5

# 日志
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# 进程管理
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = os.environ.get('GUNICORN_USER', None)
group = os.environ.get('GUNICORN_GROUP', None)

# 优雅重启
max_requests = 1000
max_requests_jitter = 50
preload_app = True
