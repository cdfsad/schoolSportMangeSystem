"""模型层测试(CustomUser 密码与 role 联动)。"""

from app01.models import CustomUser


def test_set_and_check_password(db):
    """set_password 后 check_password 应正确验证。"""
    u = CustomUser(username='t1', first_name='T', id_number='idt1', role='student')
    u.set_password('Secret@123')
    u.save()
    assert u.check_password('Secret@123') is True
    assert u.check_password('wrong-password') is False


def test_is_staff_follows_role(db):
    """role=admin/staff → is_staff=True;role=student → is_staff=False。"""
    admin = CustomUser(username='t2', first_name='A', id_number='idt2', role='admin')
    admin.set_password('x')
    admin.save()
    assert admin.is_staff is True

    student = CustomUser(username='t3', first_name='S', id_number='idt3', role='student')
    student.set_password('x')
    student.save()
    assert student.is_staff is False


def test_username_unique(db):
    """username 唯一约束(登录名不可重复)。"""
    import pytest
    from django.db import IntegrityError

    CustomUser.objects.create_user(username='dup', password='x', id_number='id1', role='student')
    with pytest.raises(IntegrityError):
        CustomUser.objects.create_user(username='dup', password='y', id_number='id2', role='student')
