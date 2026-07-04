"""预约业务逻辑服务。

关键:预约冲突校验用 `select_for_update` 行锁,防并发重复预约(P2 DRF 复用)。
P2c:approve/reject/cancel 末尾写 AuditLog,管理操作可审计。
"""

from django.db import transaction
from django.utils import timezone

from app01.models import AuditLog, Book, Campus, Place


class BookingError(Exception):
    """预约业务异常,携带错误信息列表(供视图层返回前端)。"""

    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or [message]


def _log_audit(user, action, target_model, target_id, detail=None, ip=''):
    """记录审计日志(管理操作打点,SSR 与 API 共用)。"""
    AuditLog.objects.create(
        user=user,
        action=action,
        target_model=target_model,
        target_id=str(target_id),
        detail=detail or {},
        ip=ip or None,
    )


def _resolve_campus(campus_value):
    """兼容 campus id 或名称(P1 过渡:前端可能传任一;P2 规范为 id)。"""
    if not campus_value:
        return None
    value = str(campus_value)
    if value.isdigit():
        return Campus.objects.filter(id=value).first()
    return Campus.objects.filter(name=value).first()


def check_conflict(place, date, time_slot, exclude_id=None):
    """检查同场地同时段是否已有预约。"""
    qs = Book.objects.filter(place_name=place, date=date, time=time_slot)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    return qs.exists()


def create_booking(*, user, place, date, time_slot, people, campus_value, ip=''):
    """创建预约(含冲突与容量校验)。

    参数:
        user: 预订人(CustomUser)
        place: 场地(Place)
        date/time_slot: 日期/时段字符串(兼容旧字段)
        people: 使用人数(字符串或整数)
        campus_value: 校区 id 或名称
        ip: 操作 IP(审计用)
    返回: Book 实例
    抛出: BookingError(含 errors 列表)
    """
    people_int = int(people)
    capacity = int(place.people)  # 兼容旧 CharField 字段
    campus = _resolve_campus(campus_value)
    errors = []
    with transaction.atomic():
        # 行锁防并发
        locked_place = Place.objects.select_for_update().get(pk=place.pk)
        conflict = check_conflict(locked_place, date, time_slot)
        if conflict:
            errors.append('该时间段已被预订！')
        if people_int > capacity:
            errors.append('使用人数过多！')
        if errors:
            raise BookingError('预约校验失败', errors)
        booking = Book.objects.create(
            book_name=user,
            place_name=locked_place,
            campus=campus,
            people=str(people_int),
            date=date,
            time=time_slot,
            status=0,
        )
    _log_audit(user, 'create', 'Book', booking.id, {'place': locked_place.name, 'date': date}, ip)
    return booking


def cancel_booking(*, booking_id, user, ip=''):
    """取消预约(校验归属,防越权取消他人预约)。返回 (ok, error_msg)。"""
    booking = Book.objects.filter(id=booking_id, book_name=user).first()
    if not booking:
        return False, '预约不存在或无权操作'
    place_name = booking.place_name.name if booking.place_name_id else ''
    booking.delete()
    _log_audit(user, 'cancel', 'Book', booking_id, {'place': place_name}, ip)
    return True, None


def approve_booking(*, booking_id, approver, ip=''):
    """审批通过预约(仅待审批 status==0 可通过)。返回 Book 或 None。"""
    booking = Book.objects.filter(id=booking_id, status=0).first()
    if not booking:
        return None
    booking.status = 1
    booking.approver = approver
    booking.approved_at = timezone.now()
    booking.save(update_fields=['status', 'approver', 'approved_at', 'updated_at'])
    _log_audit(approver, 'approve', 'Book', booking.id, {'place': booking.place_name.name}, ip)
    return booking


def reject_booking(*, booking_id, approver, reject_reason='', ip=''):
    """审批拒绝预约(仅待审批 status==0 可拒绝)。返回 Book 或 None。"""
    booking = Book.objects.filter(id=booking_id, status=0).first()
    if not booking:
        return None
    booking.status = 2
    booking.approver = approver
    booking.reject_reason = reject_reason
    booking.save(update_fields=['status', 'approver', 'reject_reason', 'updated_at'])
    _log_audit(
        approver,
        'reject',
        'Book',
        booking.id,
        {'place': booking.place_name.name, 'reason': reject_reason},
        ip,
    )
    return booking


def admin_cancel_booking(*, booking_id, admin=None, ip=''):
    """管理员取消任意预约(硬删除,记审计)。返回 bool。"""
    booking = Book.objects.filter(id=booking_id).first()
    if not booking:
        return False
    place_name = booking.place_name.name if booking.place_name_id else ''
    booking.delete()
    _log_audit(admin, 'cancel', 'Book', booking_id, {'place': place_name}, ip)
    return True


def list_user_bookings(user):
    """用户的预约列表。"""
    return Book.objects.filter(book_name=user).order_by('-date', '-id')


def list_all_bookings(search_status=None):
    """全部预约(管理端,可按状态过滤)。

    search_status 仅在为数字时按状态精确过滤(SSR book_admin 的 q 可能是非数字关键字,忽略)。
    """
    qs = Book.objects.all()
    if search_status is not None and str(search_status).isdigit():
        qs = qs.filter(status=int(search_status))
    return qs.order_by('-id')
