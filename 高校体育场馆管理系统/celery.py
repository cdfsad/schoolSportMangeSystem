"""Celery app 配置(P3b)。

标准 Django + Celery 整合模式:
- settings.py 的 CELERY_* 配置(namespace='CELERY')被读取
- autodiscover_tasks 自动发现各 app 的 tasks.py
- dev:CELERY_TASK_ALWAYS_EAGER=True(无 Redis 时)免 broker;prod:Redis broker
"""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '高校体育场馆管理系统.settings')

app = Celery('高校体育场馆管理系统')
# namespace='CELERY' 表示只读 settings 中 CELERY_* 开头的配置
app.config_from_object('django.conf:settings', namespace='CELERY')
# 自动发现 INSTALLED_APPS 中各 app 的 tasks.py
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
