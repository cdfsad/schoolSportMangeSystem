import pymysql

pymysql.install_as_MySQLdb()

# Celery app(P3b):必须在 Django setup 前导入,使 @shared_task 装饰器生效
from .celery import app as celery_app  # noqa: E402,F401
