"""services 层单元测试(业务逻辑核心)。"""

import pytest

from app01.models import CustomUser
from app01.services import account_service, booking_service
from app01.tests.factories import CustomUserFactory, PlaceFactory

# ===== booking_service =====


def test_create_booking_success(db):
    user = CustomUserFactory(role='student')
    place = PlaceFactory(people='10')
    booking = booking_service.create_booking(
        user=user,
        place=place,
        date='2025-06-01',
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
        date='2025-06-02',
        time_slot='10:00-11:00',
        people='5',
        campus_value=place.campus.id,
    )
    user2 = CustomUserFactory(role='student')
    with pytest.raises(booking_service.BookingError) as exc:
        booking_service.create_booking(
            user=user2,
            place=place,
            date='2025-06-02',
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
            date='2025-06-03',
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
        date='2025-06-04',
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
        date='2025-06-05',
        time_slot='10:00-11:00',
        people='3',
        campus_value=place.campus.id,
    )
    assert booking.status == 0
    approved = booking_service.approve_booking(booking_id=booking.id, approver=admin)
    assert approved.status == 1
    assert approved.approver == admin


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
