"""
高校体育场馆管理系统 - 数据模型(P1 重构)。

设计原则:
- CustomUser 继承 AbstractUser,username 作统一登录名(校内学号或校外自定义用户名)。
- 字段名尽量兼容旧版本(book_name/place_name/people/date/time/status/use),避免大改模板。
- campus 由 CharField 改为 FK(Campus),规范化。
- 软删除(is_deleted)与时间戳(created_at/updated_at)补齐。
- 外键策略:PROTECT 防误删有业务关联的对象;审批人用 SET_NULL。
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Campus(models.Model):
    """校区(取代旧 Place/Book 中硬编码的"东校区"/"白云校区"字符串)。"""

    name = models.CharField('名称', max_length=32, unique=True)
    code = models.CharField('代码', max_length=16, unique=True)
    address = models.CharField('地址', max_length=128, blank=True)
    is_active = models.BooleanField('启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '校区'
        verbose_name_plural = '校区'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """自定义用户模型。

    username 作统一登录名:校内学生用学号,校外用户用自定义用户名。
    first_name 承载"姓名"(旧 Account.username 的语义)。
    role 取代旧 Account.auth(0/1),支持更细粒度角色。
    """

    ROLE_CHOICES = [
        ('student', '学生/普通用户'),
        ('staff', '工作人员'),
        ('admin', '管理员'),
    ]
    id_number = models.CharField('学号/手机号', max_length=32, unique=True)
    role = models.CharField('角色', max_length=16, choices=ROLE_CHOICES, default='student')
    phone = models.CharField('手机号', max_length=20, blank=True)
    college = models.CharField('学院', max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.first_name or self.username

    def save(self, *args, **kwargs):
        # is_staff 跟随 role:仅 staff/admin 可进 Django admin
        self.is_staff = self.role in ('staff', 'admin')
        super().save(*args, **kwargs)


class Place(models.Model):
    """体育场地。"""

    PLACE_TYPE_CHOICES = [
        ('badminton', '羽毛球馆'),
        ('basketball', '篮球场'),
        ('table_tennis', '乒乓球馆'),
        ('gym', '健身房'),
        ('other', '其他'),
    ]
    STATUS_CHOICES = [(0, '不可用'), (1, '可使用')]

    name = models.CharField('场地', max_length=64)
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, related_name='places', verbose_name='校区')
    # people/use 保留兼容旧 views/模板;capacity 为新增结构化字段(P2 用)
    people = models.CharField('容纳人数(兼容)', max_length=32)
    capacity = models.PositiveIntegerField('容量', default=0)
    place_type = models.CharField('类型', max_length=32, choices=PLACE_TYPE_CHOICES, default='other')
    location = models.CharField('位置', max_length=128, blank=True)
    description = models.TextField('描述', blank=True)
    cover_image = models.ImageField('封面图', upload_to='place_covers/', blank=True, null=True)
    use = models.SmallIntegerField('状态', choices=STATUS_CHOICES, default=1)
    is_deleted = models.BooleanField('已删除', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '场地'
        verbose_name_plural = '场地'
        unique_together = [('name', 'campus')]

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    """可预约时段(取代 views/book.py 中硬编码的 ['10:00-11:00', ...] 列表)。"""

    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='time_slots', verbose_name='校区')
    start_time = models.TimeField('开始时间')
    end_time = models.TimeField('结束时间')
    is_active = models.BooleanField('启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '时段'
        verbose_name_plural = '时段'
        unique_together = [('campus', 'start_time', 'end_time')]
        ordering = ['sort_order', 'start_time']

    def __str__(self):
        return f'{self.start_time.strftime("%H:%M")}-{self.end_time.strftime("%H:%M")}'


class BookingRule(models.Model):
    """预约规则(P3 启用:提前可约天数、每日上限、取消时限等)。"""

    place = models.ForeignKey(
        Place, on_delete=models.CASCADE, null=True, blank=True, related_name='rules', verbose_name='适用场地'
    )
    place_type = models.CharField('场地类型', max_length=32, blank=True)
    advance_days = models.PositiveIntegerField('提前可约天数', default=7)
    daily_limit_per_user = models.PositiveIntegerField('每人每日上限', default=1)
    cancel_deadline_hours = models.PositiveIntegerField('取消时限(小时)', default=2)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '预约规则'
        verbose_name_plural = '预约规则'

    def __str__(self):
        target = self.place or self.place_type or '全局'
        return f'规则({target})'


class Book(models.Model):
    """预约记录。字段名保留兼容旧 views/模板。"""

    STATUS_CHOICES = [
        (0, '待审批'),
        (1, '已通过'),
        (2, '已拒绝'),
        (3, '已取消'),
        (4, '已完成'),
        (5, '已违约'),
    ]

    book_name = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='bookings', verbose_name='预订人')
    place_name = models.ForeignKey(Place, on_delete=models.PROTECT, related_name='bookings', verbose_name='场地')
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, related_name='bookings', verbose_name='校区')
    # 兼容旧字段(views/模板依赖)
    people = models.CharField('使用人数', max_length=32)
    date = models.CharField('日期(兼容)', max_length=32)
    time = models.CharField('时间段(兼容)', max_length=32)
    status = models.SmallIntegerField('状态', choices=STATUS_CHOICES, default=0)
    # 新增结构化字段(P2/P3 用)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, null=True, blank=True, verbose_name='时段')
    booking_date = models.DateField('预约日期', null=True, blank=True)
    # 审批
    approver = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_bookings',
        verbose_name='审批人',
    )
    approved_at = models.DateTimeField('审批时间', null=True, blank=True)
    reject_reason = models.CharField('拒绝原因', max_length=255, blank=True)
    # 软删除与时间戳
    is_deleted = models.BooleanField('已删除', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '预约'
        verbose_name_plural = '预约'
        # 显式命名索引(避免 MySQL 自动生成名超 64 字符)
        indexes = [
            models.Index(fields=['place_name', 'date', 'time'], name='idx_book_place_date_time'),
            models.Index(fields=['book_name', 'booking_date'], name='idx_book_user_date'),
        ]

    def __str__(self):
        return f'{self.book_name} - {self.place_name} ({self.date})'


class Notification(models.Model):
    """站内通知(P3 启用,配合 Celery 异步发送短信/邮件)。"""

    TYPE_CHOICES = [
        ('booking_submitted', '预约已提交'),
        ('booking_approved', '预约已通过'),
        ('booking_rejected', '预约已拒绝'),
        ('booking_reminder', '预约即将开始'),
        ('booking_no_show', '预约违约'),
        ('system', '系统通知'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', verbose_name='用户')
    type = models.CharField('类型', max_length=32, choices=TYPE_CHOICES)
    title = models.CharField('标题', max_length=128)
    content = models.TextField('内容', blank=True)
    is_read = models.BooleanField('已读', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.title}'


class AuditLog(models.Model):
    """审计日志(P2 接入:记录关键操作,便于追溯)。"""

    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs', verbose_name='操作人'
    )
    action = models.CharField('动作', max_length=32)  # create/update/delete/login 等
    target_model = models.CharField('目标模型', max_length=64)
    target_id = models.CharField('目标 ID', max_length=32)
    detail = models.JSONField('详情', default=dict, blank=True)
    ip = models.GenericIPAddressField('IP', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} {self.action} {self.target_model}'
