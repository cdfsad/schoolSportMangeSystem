"""API 层测试(P2a)。用 APIClient + JWT,覆盖 auth/资源 CRUD/权限/预约/统计。"""

import pytest
from rest_framework.test import APIClient

from app01.models import AuditLog
from app01.tests.factories import CampusFactory, CustomUserFactory, PlaceFactory

HOST = {'HTTP_HOST': '127.0.0.1'}


@pytest.fixture
def api_client(db):
    return APIClient()


def _make_authed_client(role):
    """创建独立 APIClient + role 用户登录,返回 (client, user)。

    每次 new 独立 APIClient,避免多 fixture 共享导致 token credentials 互相覆盖。
    """
    client = APIClient()
    user = CustomUserFactory(role=role)  # factory 已 set_password('Test@12345')
    resp = client.post(
        '/api/v1/auth/login/',
        {'username': user.username, 'password': 'Test@12345'},
        **HOST,
    )
    assert resp.status_code == 200, f'登录失败: {resp.content}'
    token = resp.json()['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client, user


@pytest.fixture
def admin_client(db):
    return _make_authed_client('admin')


@pytest.fixture
def student_client(db):
    return _make_authed_client('student')


# ==================== Auth ====================
def test_login_success(api_client, db):
    user = CustomUserFactory(role='student')
    r = api_client.post('/api/v1/auth/login/', {'username': user.username, 'password': 'Test@12345'}, **HOST)
    assert r.status_code == 200
    data = r.json()
    assert 'access' in data and 'refresh' in data


def test_login_wrong_password(api_client, db):
    CustomUserFactory(role='student')
    r = api_client.post('/api/v1/auth/login/', {'username': 'nobody', 'password': 'wrong'}, **HOST)
    assert r.status_code == 401


def test_me_requires_token(api_client, db):
    assert api_client.get('/api/v1/auth/me/', **HOST).status_code == 401


def test_me_authenticated(admin_client):
    c, admin = admin_client
    r = c.get('/api/v1/auth/me/', **HOST)
    assert r.status_code == 200
    assert r.json()['username'] == admin.username
    assert r.json()['role'] == 'admin'


# ==================== Places ====================
def test_list_places_authenticated(admin_client):
    c, _ = admin_client
    PlaceFactory()
    r = c.get('/api/v1/places/', **HOST)
    assert r.status_code == 200
    assert r.json()['count'] >= 1


def test_create_place_student_forbidden(student_client):
    c, _ = student_client
    r = c.post('/api/v1/places/', {'name': 'x', 'campus': 1, 'people': '5'}, **HOST)
    assert r.status_code == 403


def test_create_place_admin_ok(admin_client):
    c, _ = admin_client
    campus = CampusFactory()
    r = c.post(
        '/api/v1/places/',
        {'name': '测试场地', 'campus': campus.id, 'people': '10', 'use': 1},
        **HOST,
    )
    assert r.status_code == 201


# ==================== Books ====================
def test_create_booking_success(admin_client):
    c, _ = admin_client
    place = PlaceFactory(people='10')
    r = c.post(
        '/api/v1/books/',
        {
            'place': place.id,
            'date': '2025-07-01',
            'bkTime': '10:00-11:00',
            'people': '5',
            'campus': place.campus.id,
        },
        **HOST,
    )
    assert r.status_code == 201


def test_create_booking_conflict_rejected(admin_client):
    c, _ = admin_client
    place = PlaceFactory(people='10')
    payload = {
        'place': place.id,
        'date': '2025-07-02',
        'bkTime': '10:00-11:00',
        'people': '3',
        'campus': place.campus.id,
    }
    assert c.post('/api/v1/books/', payload, **HOST).status_code == 201
    r2 = c.post('/api/v1/books/', payload, **HOST)
    assert r2.status_code == 400


def test_cancel_own_booking(admin_client):
    c, _ = admin_client
    place = PlaceFactory(people='10')
    bid = c.post(
        '/api/v1/books/',
        {
            'place': place.id,
            'date': '2025-07-03',
            'bkTime': '10:00-11:00',
            'people': '2',
            'campus': place.campus.id,
        },
        **HOST,
    ).json()['id']
    r = c.post(f'/api/v1/books/{bid}/cancel/', **HOST)
    assert r.status_code == 200


def test_approve_booking_admin(admin_client, student_client):
    c_admin, _ = admin_client
    c_stu, _ = student_client
    place = PlaceFactory(people='10')
    bid = c_stu.post(
        '/api/v1/books/',
        {
            'place': place.id,
            'date': '2025-07-04',
            'bkTime': '10:00-11:00',
            'people': '2',
            'campus': place.campus.id,
        },
        **HOST,
    ).json()['id']
    r = c_admin.post(f'/api/v1/books/{bid}/approve/', **HOST)
    assert r.status_code == 200
    assert r.json()['status'] == 1


def test_student_only_sees_own_bookings(student_client, admin_client):
    c_stu, stu = student_client
    c_admin, _ = admin_client
    place = PlaceFactory(people='10')
    # admin 创建预约
    c_admin.post(
        '/api/v1/books/',
        {
            'place': place.id,
            'date': '2025-07-05',
            'bkTime': '10:00-11:00',
            'people': '4',
            'campus': place.campus.id,
        },
        **HOST,
    )
    # student 查看预约:只看到自己的(此处为 0)
    r = c_stu.get('/api/v1/books/', **HOST)
    assert r.status_code == 200
    assert r.json()['count'] == 0


# ==================== 权限矩阵 ====================
def test_users_admin_only(student_client):
    c, _ = student_client
    assert c.get('/api/v1/users/', **HOST).status_code == 403


def test_audit_log_admin_only(student_client):
    c, _ = student_client
    assert c.get('/api/v1/audit-logs/', **HOST).status_code == 403


def test_admin_can_list_users(admin_client):
    c, _ = admin_client
    r = c.get('/api/v1/users/', **HOST)
    assert r.status_code == 200


# ==================== 统计 ====================
def test_statistics(admin_client):
    c, _ = admin_client
    r = c.get('/api/v1/statistics/', **HOST)
    assert r.status_code == 200
    data = r.json()
    assert 'legend' in data and 'series' in data


# ==================== 拒绝预约(P2c) ====================
def test_reject_booking_admin(admin_client, student_client):
    c_admin, _ = admin_client
    c_stu, _ = student_client
    place = PlaceFactory(people='10')
    bid = c_stu.post(
        '/api/v1/books/',
        {'place': place.id, 'date': '2025-08-01', 'bkTime': '10:00-11:00', 'people': '2', 'campus': place.campus.id},
        **HOST,
    ).json()['id']
    before = AuditLog.objects.filter(action='reject').count()
    r = c_admin.post(f'/api/v1/books/{bid}/reject/', {'reject_reason': '时段冲突'}, **HOST)
    assert r.status_code == 200
    assert r.json()['status'] == 2
    assert r.json()['reject_reason'] == '时段冲突'
    assert AuditLog.objects.filter(action='reject').count() == before + 1


def test_reject_non_pending_returns_400(admin_client, student_client):
    c_admin, _ = admin_client
    c_stu, _ = student_client
    place = PlaceFactory(people='10')
    bid = c_stu.post(
        '/api/v1/books/',
        {'place': place.id, 'date': '2025-08-02', 'bkTime': '10:00-11:00', 'people': '2', 'campus': place.campus.id},
        **HOST,
    ).json()['id']
    # 先通过再拒绝 → 400(仅待审批可拒绝)
    c_admin.post(f'/api/v1/books/{bid}/approve/', **HOST)
    r = c_admin.post(f'/api/v1/books/{bid}/reject/', {'reject_reason': 'x'}, **HOST)
    assert r.status_code == 400


def test_reject_booking_student_forbidden(student_client, admin_client):
    c_stu, _ = student_client
    c_admin, _ = admin_client
    place = PlaceFactory(people='10')
    bid = c_admin.post(
        '/api/v1/books/',
        {'place': place.id, 'date': '2025-08-03', 'bkTime': '10:00-11:00', 'people': '2', 'campus': place.campus.id},
        **HOST,
    ).json()['id']
    r = c_stu.post(f'/api/v1/books/{bid}/reject/', **HOST)
    assert r.status_code == 403


# ==================== AuditLog 打点(P2c) ====================
def test_approve_writes_audit_log(admin_client, student_client):
    c_admin, _ = admin_client
    c_stu, _ = student_client
    place = PlaceFactory(people='10')
    bid = c_stu.post(
        '/api/v1/books/',
        {'place': place.id, 'date': '2025-08-04', 'bkTime': '10:00-11:00', 'people': '2', 'campus': place.campus.id},
        **HOST,
    ).json()['id']
    before = AuditLog.objects.filter(action='approve').count()
    c_admin.post(f'/api/v1/books/{bid}/approve/', **HOST)
    assert AuditLog.objects.filter(action='approve').count() == before + 1


def test_cancel_writes_audit_log(admin_client):
    c, _ = admin_client
    place = PlaceFactory(people='10')
    bid = c.post(
        '/api/v1/books/',
        {'place': place.id, 'date': '2025-08-05', 'bkTime': '10:00-11:00', 'people': '2', 'campus': place.campus.id},
        **HOST,
    ).json()['id']
    before = AuditLog.objects.count()
    c.post(f'/api/v1/books/{bid}/cancel/', **HOST)
    assert AuditLog.objects.count() >= before + 1


# ==================== 校区 CRUD(P2c) ====================
def test_campus_list_authenticated(student_client):
    c, _ = student_client
    CampusFactory()
    r = c.get('/api/v1/campuses/', **HOST)
    assert r.status_code == 200
    assert r.json()['count'] >= 1


def test_campus_create_admin_ok(admin_client):
    c, _ = admin_client
    r = c.post('/api/v1/campuses/', {'name': '新校区', 'code': 'new', 'sort_order': 1}, **HOST)
    assert r.status_code == 201


def test_campus_create_student_forbidden(student_client):
    c, _ = student_client
    r = c.post('/api/v1/campuses/', {'name': 'x', 'code': 'x'}, **HOST)
    assert r.status_code == 403


def test_campus_update_destroy_admin(admin_client):
    c, _ = admin_client
    campus = CampusFactory(name='旧校区', code='old')
    r = c.patch(f'/api/v1/campuses/{campus.id}/', {'name': '改后'}, **HOST)
    assert r.status_code == 200
    r2 = c.delete(f'/api/v1/campuses/{campus.id}/', **HOST)
    assert r2.status_code == 204


def test_campus_destroy_student_forbidden(student_client):
    c, _ = student_client
    campus = CampusFactory()
    r = c.delete(f'/api/v1/campuses/{campus.id}/', **HOST)
    assert r.status_code == 403
