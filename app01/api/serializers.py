"""DRF 序列化器(P2a)。"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from app01.models import AuditLog, Book, BookingRule, Campus, CustomUser, Notification, Place, TimeSlot


# ===== Auth =====
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT 登录:payload 注入 role/user_id/name,前端免二次查询。"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['user_id'] = user.id
        token['name'] = user.first_name or user.username
        return token


# ===== 资源 =====
class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = ['id', 'name', 'code', 'address', 'is_active', 'sort_order']


class CustomUserSerializer(serializers.ModelSerializer):
    """用户(学生管理)。password write_only,创建时默认 username=id_number。"""

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'id_number',
            'role',
            'phone',
            'college',
            'password',
            'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False, 'allow_blank': True},
        }

    def create(self, validated):
        password = validated.pop('password', None)
        # 学生用学号作登录名
        if not validated.get('username'):
            validated['username'] = validated.get('id_number') or validated.get('phone')
        user = CustomUser(**validated)
        user.set_password(password or CustomUser.objects.make_random_password(length=12))
        user.save()
        return user

    def update(self, instance, validated):
        password = validated.pop('password', None)
        for key, value in validated.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class PlaceSerializer(serializers.ModelSerializer):
    campus_name = serializers.CharField(source='campus.name', read_only=True)

    class Meta:
        model = Place
        fields = [
            'id',
            'name',
            'campus',
            'campus_name',
            'people',
            'capacity',
            'place_type',
            'location',
            'use',
            'is_deleted',
        ]
        read_only_fields = ['is_deleted']


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'campus', 'start_time', 'end_time', 'is_active', 'sort_order']


class BookingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRule
        fields = [
            'id',
            'place',
            'place_type',
            'advance_days',
            'daily_limit_per_user',
            'cancel_deadline_hours',
            'is_active',
        ]


class BookReadSerializer(serializers.ModelSerializer):
    """预约读取(嵌套显示关联,前端免多次请求)。"""

    book_name = CustomUserSerializer(read_only=True)
    place_name = PlaceSerializer(read_only=True)
    campus_name = serializers.CharField(source='campus.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'book_name',
            'place_name',
            'campus',
            'campus_name',
            'people',
            'date',
            'time',
            'status',
            'status_display',
            'approver',
            'approved_at',
            'reject_reason',
            'created_at',
        ]
        read_only_fields = fields


class BookCreateSerializer(serializers.Serializer):
    """预约创建:仅校验字段,实际逻辑走 booking_service(含 select_for_update 冲突锁)。"""

    place = serializers.PrimaryKeyRelatedField(queryset=Place.objects.filter(is_deleted=False))
    date = serializers.CharField()
    bkTime = serializers.CharField()
    people = serializers.CharField()
    campus = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated):
        # 局部 import 避免循环
        from app01.services import booking_service
        from app01.services.booking_service import BookingError

        try:
            return booking_service.create_booking(
                user=self.context['request'].user,
                place=validated['place'],
                date=validated['date'],
                time_slot=validated['bkTime'],
                people=validated['people'],
                campus_value=validated.get('campus', ''),
            )
        except BookingError as exc:
            raise serializers.ValidationError({'errors': exc.errors}) from exc


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'type', 'type_display', 'title', 'content', 'is_read', 'created_at']
        read_only_fields = ['type', 'title', 'content', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default='')

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'username',
            'action',
            'target_model',
            'target_id',
            'detail',
            'ip',
            'created_at',
        ]
