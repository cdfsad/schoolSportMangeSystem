"""登录流程测试(校内学号登录 + 验证码)。"""

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore

from app01.tests.factories import CustomUserFactory


def _set_captcha(client):
    """给 client 的 session 设固定验证码(绕过随机生成)。"""
    s = SessionStore()
    s['img_code'] = 'ABCD'
    s.save()
    client.cookies[settings.SESSION_COOKIE_NAME] = s.session_key


def _make_user(username, role='student', password='Test@12345'):
    user = CustomUserFactory(username=username, id_number=username, role=role)
    user.set_password(password)
    user.save()
    return user


def test_student_login_success(client, db, host):
    """校内学号 + 密码 + 验证码正确 → 重定向 /common/。"""
    _make_user('2020123456', role='student')
    _set_captcha(client)
    r = client.post(
        '/login/',
        {
            'id_number': '2020123456',
            'password': 'Test@12345',
            'code': 'ABCD',
        },
        **host,
    )
    assert r.status_code == 302
    assert r.url == '/common/'


def test_admin_login_redirects_to_admin(client, db, host):
    """管理员登录 → 重定向 /admin/。"""
    _make_user('2020999', role='admin')
    _set_captcha(client)
    r = client.post(
        '/login/',
        {
            'id_number': '2020999',
            'password': 'Test@12345',
            'code': 'ABCD',
        },
        **host,
    )
    assert r.status_code == 302
    assert r.url == '/admin/'


def test_login_wrong_password(client, db, host):
    """密码错误 → 返回登录页(200,表单错误)。"""
    _make_user('2020123457', role='student')
    _set_captcha(client)
    r = client.post(
        '/login/',
        {
            'id_number': '2020123457',
            'password': 'wrong',
            'code': 'ABCD',
        },
        **host,
    )
    assert r.status_code == 200


def test_login_wrong_captcha(client, db, host):
    """验证码错误 → 返回登录页。"""
    _make_user('2020123458', role='student')
    _set_captcha(client)
    r = client.post(
        '/login/',
        {
            'id_number': '2020123458',
            'password': 'Test@12345',
            'code': 'WRONG',
        },
        **host,
    )
    assert r.status_code == 200


def test_login_nonexistent_user(client, db, host):
    """不存在的学号 → 返回登录页。"""
    _set_captcha(client)
    r = client.post(
        '/login/',
        {
            'id_number': '0000000',
            'password': 'Test@12345',
            'code': 'ABCD',
        },
        **host,
    )
    assert r.status_code == 200
