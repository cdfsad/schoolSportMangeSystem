"""services 层单元测试(业务逻辑核心)。"""

from datetime import date, datetime, timedelta

import pytest
from django.utils import timezone

from app01.models import Book, BookingRule, CustomUser, Notification
from app01.services import account_service, booking_service
from app01.tests.factories import CustomUserFactory, PlaceFactory


def _future(days=3):
    """未来日期字符串(ISO),默认 3 天后(在默认 advance_days=7 窗口内,且远超 cancel_deadline=2h)。"""
    return (date.today() + timedelta(days=days)).isoformat()


# ===== booking_service =====


def test_create_booking_success(db):
    user = CustomUserFactory(role='student')
    place = PlaceFactory(people='10')
    booking = booking_service.create_booking(
        user=user,
        place=place,
        date=_future(3),
        time_slot='10:00-11:00',
        people='5',
        campus_value=place.campus.id,
    )
    assert booking.id is not None
    assert booking.status == 0
    assert booking.people == '5'


def test_create_booking_conflict_rejected(db):
    """同场地同时段重复预约应被拒。"""
    user = CustomUserFactory(role='student')
    place = PlaceFactory(people='10')
    booking_service.create_booking(
        user=user,
        place=place,
        date=_future(4),
        time_slot='10:00-11:00',
        people='5',
        campus_value=place.campus.id,
    )
    user2 = CustomUserFactory(role='student')
    with pytest.raises(booking_service.BookingError) as exc:
        booking_service.create_booking(
            user=user2,
            place=place,
            date=_future(4),
            time_slot='10:00-11:00',
            people='3',
            campus_value=place.campus.id,
        )
    assert any('已被预订' in e for e in exc.value.errors)


def test_create_booking_over_capacity_rejected(db):
    """使用人数超容量应被拒。"""
    user = CustomUserFactory(role='student')
    place = PlaceFactory(people='5')
    with pytest.raises(booking_service.BookingError) as exc:
        booking_service.create_booking(
            user=user,
            place=place,
            date=_future(5),
            time_slot='10:00-11:00',
            people='10',
            campus_value=place.campus.id,
        )
    assert any('人数过多' in e for e in exc.value.errors)


def test_cancel_booking_ownership_check(db):
    """非预约人无法取消;本人可取消。"""
    owner = CustomUserFactory(role='student')
    attacker = CustomUserFactory(username='attacker', id_number='atk1', role='student')
    place = PlaceFactory()
    booking = booking_service.create_booking(
        user=owner,
        place=place,
        date=_future(6),
        time_slot='10:00-11:00',
        people='2',
        campus_value=place.campus.id,
    )
    ok, _ = booking_service.cancel_booking(booking_id=booking.id, user=attacker)
    assert ok is False
    ok, _ = booking_service.cancel_booking(booking_id=booking.id, user=owner)
    assert ok is True


def test_approve_booking(db):
    user = CustomUserFactory(role='student')
    admin = CustomUserFactory(username='admin2', id_number='adm2', role='admin')
    place = PlaceFactory()
    booking = booking_service.create_booking(
        user=user,
        place=place,
        date=_future(3),
        time_slot='10:00-11:00',
        people='3',
        campus_value=place.campus.id,
    )
    assert booking.status == 0
    approved = booking_service.approve_booking(booking_id=booking.id, approver=admin)
    assert approved.status == 1
    assert approved.approver == admin


# ===== P3a: BookingRule 接入 =====


def _make_rule(**kwargs):
    """创建/覆盖一条全局规则(测试隔离,不依赖种子 migration)。"""
    BookingRule.objects.filter(place__isnull=True, place_type='').delete()
    defaults = {'advance_days': 7, 'daily_limit_per_user': 1, 'cancel_deadline_hours': 2, 'is_active': True}
    defaults.update(kwargs)
    return BookingRule.objects.create(place=None, place_type='', **defaults)


def test_create_booking_advance_days_exceeded(db):
    """超过 advance_days 的预约应被拒。"""
    _make_rule(advance_days=7)
    user = CustomUserFactory(role='student')
    place = PlaceFactory(people='10')
    with pytest.raises(booking_service.BookingError) as exc:
        booking_service.create_booking(
            user=user,
            place=place,
            date=_future(30),
            time_slot='10:00-11:00',
            people='2',
            campus_value=place.campus.id,
        )
    assert any('天内' in e for e in exc.value.errors)


def test_create_booking_daily_limit_exceeded(db):
    """同一用户同日预约超 daily_limit 应被拒(用不同时段隔离冲突检查)。"""
    _make_rule(daily_limit_per_user=1)
    user = CustomUserFactory(role='student')
    place = PlaceFactory(people='10')
    booking_service.create_booking(
        user=user,
        place=place,
        date=_future(3),
        time_slot='10:00-11:00',
        people='2',
        campus_value=place.campus.id,
    )
    with pytest.raises(booking_service.BookingError) as exc:
        booking_service.create_booking(
            user=user,
            place=place,
            date=_future(3),
            time_slot='11:00-12:00',  # 不同时段
            people='2',
            campus_value=place.campus.id,
        )
    assert any('每天最多' in e for e in exc.value.errors)


def test_cancel_booking_past_deadline(db):
    """过取消截止的预约不可取消。"""
    _make_rule(cancel_deadline_hours=2)
    user = CustomUserFactory(role='student')
    place = PlaceFactory()
    start = timezone.now() + timedelta(hours=1)  # 1 小时后开始,deadline=2h 前已过
    booking = Book.objects.create(
        book_name=user,
        place_name=place,
        campus=place.campus,
        people='2',
        date=start.strftime('%Y-%m-%d'),
        time=f'{start.strftime("%H:%M")}-{(start + timedelta(hours=1)).strftime("%H:%M")}',
        status=1,
    )
    ok, msg = booking_service.cancel_booking(booking_id=booking.id, user=user)
    assert ok is False
    assert '取消时限' in (msg or '')


def test_no_rule_allows_booking(db):
    """无任何规则时不阻断(兼容空表)。"""
    BookingRule.objects.all().delete()
    user = CustomUserFactory(role='student')
    place = PlaceFactory(people='10')
    booking = booking_service.create_booking(
        user=user,
        place=place,
        date=_future(3),
        time_slot='10:00-11:00',
        people='2',
        campus_value=place.campus.id,
    )
    assert booking.id is not None


# ===== P3a: Notification producers =====


def test_create_booking_notifies_user(db):
    _make_rule()
    user = CustomUserFactory(role='student')
    place = PlaceFactory(people='10')
    before = Notification.objects.filter(user=user).count()
    booking_service.create_booking(
        user=user,
        place=place,
        date=_future(3),
        time_slot='10:00-11:00',
        people='2',
        campus_value=place.campus.id,
    )
    assert Notification.objects.filter(user=user).count() == before + 1
    assert Notification.objects.filter(user=user, type='booking_submitted').exists()


def test_approve_booking_notifies_user(db):
    _make_rule()
    user = CustomUserFactory(role='student')
    admin = CustomUserFactory(username='admin_n', id_number='admn', role='admin')
    place = PlaceFactory()
    booking = booking_service.create_booking(
        user=user,
        place=place,
        date=_future(3),
        time_slot='10:00-11:00',
        people='2',
        campus_value=place.campus.id,
    )
    Notification.objects.filter(user=user).delete()  # 排除提交通知
    booking_service.approve_booking(booking_id=booking.id, approver=admin)
    assert Notification.objects.filter(user=user, type='booking_approved').exists()


def test_reject_booking_notifies_user_with_reason(db):
    _make_rule()
    user = CustomUserFactory(role='student')
    admin = CustomUserFactory(username='admin_r', id_number='admr', role='admin')
    place = PlaceFactory()
    booking = booking_service.create_booking(
        user=user,
        place=place,
        date=_future(3),
        time_slot='10:00-11:00',
        people='2',
        campus_value=place.campus.id,
    )
    booking_service.reject_booking(booking_id=booking.id, approver=admin, reject_reason='场地维护')
    n = Notification.objects.filter(user=user, type='booking_rejected').first()
    assert n is not None
    assert '场地维护' in n.content


# ===== account_service =====


def test_authenticate_success_and_failure(db):
    u = CustomUser(username='auth_user', first_name='T', id_number='idauth', role='student')
    u.set_password('Secret@1')
    u.save()
    assert account_service.authenticate('auth_user', 'Secret@1') == u
    assert account_service.authenticate('auth_user', 'wrong') is None
    assert account_service.authenticate('nonexist', 'Secret@1') is None


def test_change_password(db):
    u = CustomUser(username='pwd_user', first_name='T', id_number='idpwd', role='student')
    u.set_password('Old@123')
    u.save()
    ok, _ = account_service.change_password(user=u, old_password='Old@123', new_password='New@456')
    assert ok is True
    assert u.check_password('New@456') is True
    # 旧密码错误
    ok, msg = account_service.change_password(user=u, old_password='wrong', new_password='X@9')
    assert ok is False
