"""IDOR 与 CSRF 安全测试(P0/P1 安全核心)。"""

from app01.models import Book
from app01.tests.factories import CustomUserFactory, PlaceFactory


def test_change_pwd_uses_session_id_not_url(client_as, db, host):
    """改密接口从 session 取用户 id(URL 无 nid 参数,防 IDOR 改他人密码)。"""
    user = CustomUserFactory(role='student')
    user.set_password('Old@12345')
    user.save()
    c = client_as(user)
    r = c.post(
        '/account/reset/',
        {
            'old_password': 'Old@12345',
            'new_password': 'New@12345',
            'confirm_password': 'New@12345',
        },
        **host,
    )
    assert r.status_code == 302  # 改密成功重定向到登录页
    user.refresh_from_db()
    assert user.check_password('New@12345') is True
    assert user.check_password('Old@12345') is False


def test_place_book_uses_session_id(client_as, db, host):
    """预约页从 session 取用户 id(URL 无 nid,防替他人预约)。"""
    student = CustomUserFactory(role='student')
    place = PlaceFactory()
    c = client_as(student)
    r = c.get(f'/place/{place.id}/book/', **host)
    assert r.status_code == 200


def test_student_cannot_cancel_others_booking(client_as, db, host):
    """学生不能取消他人预约(book_delete1 归属校验)。"""
    owner = CustomUserFactory(username='owner', id_number='own1')
    attacker = CustomUserFactory(username='attacker', id_number='atk1')
    place = PlaceFactory()
    booking = Book.objects.create(
        book_name=owner,
        place_name=place,
        campus=place.campus,
        people='5',
        date='2025-01-01',
        time='10:00-11:00',
        status=0,
    )
    c = client_as(attacker)  # 另一学生尝试取消 owner 的预约
    r = c.post('/book/delete1/', {'stu_did': booking.id}, **host)
    assert r.json()['status'] is False  # 拒绝
    assert Book.objects.filter(id=booking.id).exists()  # 预约未被删除


def test_owner_can_cancel_own_booking(client_as, db, host):
    """预约本人可取消自己的预约。"""
    owner = CustomUserFactory(username='owner2', id_number='own2')
    place = PlaceFactory()
    booking = Book.objects.create(
        book_name=owner,
        place_name=place,
        campus=place.campus,
        people='5',
        date='2025-01-02',
        time='10:00-11:00',
        status=0,
    )
    c = client_as(owner)
    r = c.post('/book/delete1/', {'stu_did': booking.id}, **host)
    assert r.json()['status'] is True
    assert not Book.objects.filter(id=booking.id).exists()


def test_post_without_csrf_token_rejected(db, host):
    """enforce_csrf_checks 下,登录态 POST 缺 CSRF token 应 403。"""
    from django.conf import settings
    from django.contrib.sessions.backends.db import SessionStore
    from django.test import Client

    admin = CustomUserFactory(role='admin')
    c = Client(enforce_csrf_checks=True)
    s = SessionStore()
    s['info'] = {'id': admin.id, 'name': admin.first_name, 'role': 'admin'}
    s.save()
    c.cookies[settings.SESSION_COOKIE_NAME] = s.session_key
    r = c.post('/student/delete/', {'uid': 99999}, **host)
    assert r.status_code == 403


def test_get_delete_does_not_execute(db, host):
    """GET 访问删除接口不应执行删除(后端只接受 POST)。"""
    from django.conf import settings
    from django.contrib.sessions.backends.db import SessionStore
    from django.test import Client

    from app01.tests.factories import CustomUserFactory

    admin = CustomUserFactory(role='admin')
    c = Client()
    s = SessionStore()
    s['info'] = {'id': admin.id, 'name': admin.first_name, 'role': 'admin'}
    s.save()
    c.cookies[settings.SESSION_COOKIE_NAME] = s.session_key
    admin_id = admin.id
    r = c.get('/student/delete/?uid=' + str(admin_id), **host)
    data = r.json()
    # GET 到达视图但 POST.get('uid')=None,返回缺参数;账号未被删
    assert data['status'] is False
    from app01.models import CustomUser

    assert CustomUser.objects.filter(id=admin_id).exists()
