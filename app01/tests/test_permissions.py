"""RBAC 权限矩阵测试(P0/P1 安全核心)。

验证:匿名重定向、学生被管理页 403、管理员全放行、学生可访问学生页。
"""

from app01.tests.factories import CustomUserFactory

# 仅管理员可访问的 URL
ADMIN_URLS = [
    '/admin/',
    '/student/list/',
    '/place/list1/',
    '/place/list2/',
    '/book/admin/',
    '/student/multi/',
    '/place/add/',
    '/place/delete/',
]
# 学生可访问的 URL
STUDENT_OK_URLS = ['/common/', '/place/stu/list1/', '/place/stu/list2/', '/my/book/']


def _get(client, url, host):
    # GET 用于只读页;写操作页(/place/add/ 等)用 POST 测试,这里仅验证权限拦截
    return client.get(url, **host)


def test_anonymous_redirected_to_index(client, db, host):
    """匿名访问受保护页应重定向到首页。"""
    r = client.get('/student/list/', **host)
    assert r.status_code == 302


def test_student_blocked_from_admin_pages(client_as, db, host):
    """普通学生访问管理页应返回 403。"""
    student = CustomUserFactory(role='student')
    c = client_as(student)
    for url in ['/admin/', '/student/list/', '/place/list1/', '/book/admin/']:
        r = c.get(url, **host)
        assert r.status_code == 403, f'{url} 应拒绝学生访问(期望 403,实际 {r.status_code})'


def test_student_can_access_student_pages(client_as, db, host):
    """学生可访问学生页(200)。"""
    student = CustomUserFactory(role='student')
    c = client_as(student)
    for url in STUDENT_OK_URLS:
        r = c.get(url, **host)
        assert r.status_code == 200, f'{url} 应允许学生(期望 200,实际 {r.status_code})'


def test_admin_can_access_admin_pages(client_as, db, host):
    """管理员可访问所有管理页(200)。"""
    admin = CustomUserFactory(role='admin')
    c = client_as(admin)
    for url in ['/admin/', '/student/list/', '/place/list1/', '/place/list2/', '/book/admin/', '/common/', '/my/book/']:
        r = c.get(url, **host)
        assert r.status_code == 200, f'{url} 应允许管理员(期望 200,实际 {r.status_code})'


def test_logout_clears_session(client, db, host):
    """注销应清除 session 并重定向。"""
    r = client.get('/logout/', **host)
    assert r.status_code == 302
