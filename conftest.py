"""pytest 全局 fixture。"""

import pytest
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.test import Client


@pytest.fixture
def client_as(db):
    """返回工厂函数:传入 user 返回登录态 Client(通过 session 模拟登录,绕过验证码)。

    用法:
        c = client_as(admin_user)   # 登录态
        c = client_as(None)         # 匿名
    所有请求自动加 HTTP_HOST='127.0.0.1'(ALLOWED_HOSTS 允许)。
    """

    def _make(user=None):
        c = Client(enforce_csrf_checks=False)
        if user is not None:
            s = SessionStore()
            s['info'] = {
                'id': user.id,
                'name': user.first_name or user.username,
                'role': user.role,
            }
            s.save()
            c.cookies[settings.SESSION_COOKIE_NAME] = s.session_key
        return c

    return _make


@pytest.fixture
def host():
    """统一 HTTP_HOST,避免 ALLOWED_HOSTS 拒绝。"""
    return {'HTTP_HOST': '127.0.0.1'}
