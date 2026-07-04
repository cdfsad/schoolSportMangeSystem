"""Celery 异步任务(P3b)。

- send_notification:站内通知异步写入(解耦主请求,经 _notify 调用)
- scan_no_shows:定时扫描已过期的已通过预约,标记违约(status=5)+ 通知

dev(CELERY_TASK_ALWAYS_EAGER=True):.delay() 同步执行,免 broker;
prod:走 Redis broker + 独立 worker/beat 容器。
"""

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from app01.models import Book, CustomUser, Notification


@shared_task
def send_notification(user_id, ntype, title, content=''):
    """异步创建站内通知。取 user_id(可序列化),内部查 user。"""
    user = CustomUser.objects.filter(id=user_id).first()
    if user is None:
        return
    Notification.objects.create(user=user, type=ntype, title=title, content=content)


@shared_task
def scan_no_shows(grace_minutes=30):
    """扫描已过开始时间 + 宽限期的已通过预约(status=1),标记违约(status=5)+ 通知。

    返回标记条数。beat 每 30 分钟触发;也可经 `manage.py scan_no_shows` 手动跑。
    """
    # 延迟导入避循环(booking_service._notify 反向调本模块 send_notification)
    from app01.services.booking_service import _notify, _parse_booking_start

    now = timezone.now()
    threshold = now - timedelta(minutes=grace_minutes)
    count = 0
    for booking in Book.objects.filter(status=1).select_related('book_name', 'place_name'):
        start = _parse_booking_start(booking)
        # start + grace 已过(等价于 start < threshold),且 start 解析成功
        if start and start < threshold:
            booking.status = 5
            booking.save(update_fields=['status', 'updated_at'])
            _notify(
                booking.book_name,
                'booking_no_show',
                f'预约违约:{booking.place_name.name} {booking.date} {booking.time}',
                '预约已过开始时间,系统标记为违约。',
            )
            count += 1
    return count
