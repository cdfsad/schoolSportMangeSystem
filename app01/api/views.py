"""DRF 视图(P2a)。ViewSet 保持薄,业务逻辑复用 app01/services/。"""

from django.db.models import Count
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from app01 import models
from app01.api.filters import BookFilter
from app01.api.permissions import IsAdmin, IsOwnerOrAdmin
from app01.api.serializers import (
    AuditLogSerializer,
    BookCreateSerializer,
    BookingRuleSerializer,
    BookReadSerializer,
    CampusSerializer,
    CustomUserSerializer,
    MyTokenObtainPairSerializer,
    NotificationSerializer,
    PlaceSerializer,
    TimeSlotSerializer,
)
from app01.services import account_service, booking_service, place_service


def _client_ip(request):
    """从请求中提取客户端 IP(审计用,空字符串兜底)。"""
    return request.META.get('REMOTE_ADDR', '') or ''


# ==================== Auth ====================
class MyTokenObtainPairView(TokenObtainPairView):
    """JWT 登录(自定义 serializer,payload 加 role)。"""

    serializer_class = MyTokenObtainPairSerializer


class LogoutView(APIView):
    """登出:blacklist refresh token。"""

    def post(self, request):
        token = request.data.get('refresh')
        if not token:
            return Response({'detail': '缺少 refresh token'}, status=400)
        try:
            RefreshToken(token).blacklist()
        except Exception:
            return Response({'detail': '无效的 refresh token'}, status=400)
        return Response({'detail': '已登出'})


class MeView(APIView):
    """当前登录用户信息。"""

    def get(self, request):
        return Response(CustomUserSerializer(request.user).data)


class ChangePasswordView(APIView):
    """修改当前用户密码(调 account_service)。"""

    def post(self, request):
        old = request.data.get('old_password')
        new = request.data.get('new_password')
        ok, msg = account_service.change_password(user=request.user, old_password=old, new_password=new)
        if not ok:
            return Response({'detail': msg}, status=400)
        return Response({'detail': '密码已修改'})


class UserImportView(APIView):
    """Excel 批量导入学生(调 account_service)。"""

    permission_classes = [IsAdmin]

    def post(self, request):
        file_obj = request.FILES.get('exc') or request.FILES.get('file')
        if not file_obj:
            return Response({'detail': '请上传 Excel 文件'}, status=400)
        result = account_service.import_students_from_excel(file_obj)
        return Response(result)


# ==================== ViewSets ====================
class CampusViewSet(viewsets.ModelViewSet):
    """校区:GET 所有人 / CUD 管理员。"""

    queryset = models.Campus.objects.all().order_by('sort_order', 'id')
    serializer_class = CampusSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = models.Campus.objects.all().order_by('sort_order', 'id')
        # 非管理员仅见启用校区
        if self.request.user.role != 'admin':
            qs = qs.filter(is_active=True)
        return qs


class CustomUserViewSet(viewsets.ModelViewSet):
    """用户管理(仅管理员)。"""

    queryset = models.CustomUser.objects.all().order_by('-id')
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdmin]
    search_fields = ['first_name', 'id_number', 'username']
    ordering_fields = ['id', 'date_joined']


class PlaceViewSet(viewsets.ModelViewSet):
    """场地:GET 所有人 / CUD 管理员。"""

    queryset = models.Place.objects.select_related('campus')
    serializer_class = PlaceSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'time_slots'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = place_service.list_places(only_active=False).select_related('campus')
        campus = self.request.query_params.get('campus')
        search = self.request.query_params.get('search')
        if campus:
            qs = qs.filter(campus_id=campus)
        if search:
            qs = qs.filter(name__contains=search)
        return qs

    def perform_destroy(self, instance):
        place_service.soft_delete_place(instance.id)

    @action(detail=True, methods=['get'], url_path='time-slots')
    def time_slots(self, request, pk=None):
        place = self.get_object()
        slots = place_service.get_time_slots(place.campus_id)
        return Response(TimeSlotSerializer(slots, many=True).data)


class TimeSlotViewSet(viewsets.ModelViewSet):
    """时段:GET 所有人 / CUD 管理员。"""

    queryset = models.TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    filterset_fields = ['campus']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]


class BookViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """预约:GET(自己/管理员) / POST(调 service) / cancel / approve / DELETE(管理员)。"""

    queryset = models.Book.objects.select_related('book_name', 'place_name', 'campus', 'approver')
    filterset_class = BookFilter

    def get_serializer_class(self):
        return BookCreateSerializer if self.action == 'create' else BookReadSerializer

    def get_permissions(self):
        if self.action in ('approve', 'reject'):
            return [IsAdmin()]
        if self.action == 'cancel':
            return [IsOwnerOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset().order_by('-id')
        # 学生/工作人员仅看自己的预约;管理员看全部
        if self.request.user.role != 'admin':
            qs = qs.filter(book_name=self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookReadSerializer(booking).data, status=201)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        ok, msg = booking_service.cancel_booking(booking_id=pk, user=request.user, ip=_client_ip(request))
        if not ok:
            return Response({'detail': msg}, status=400)
        return Response({'status': 'cancelled'})

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        booking = booking_service.approve_booking(booking_id=pk, approver=request.user, ip=_client_ip(request))
        if not booking:
            return Response({'detail': '预约不存在或不可审批'}, status=400)
        return Response(BookReadSerializer(booking).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝预约(仅待审批,body 可带 reject_reason)。"""
        reason = request.data.get('reject_reason', '')
        booking = booking_service.reject_booking(
            booking_id=pk,
            approver=request.user,
            reject_reason=reason,
            ip=_client_ip(request),
        )
        if not booking:
            return Response({'detail': '预约不存在或不可拒绝'}, status=400)
        return Response(BookReadSerializer(booking).data)

    def perform_destroy(self, instance):
        """管理员删除预约(走 service,记审计)。"""
        booking_service.admin_cancel_booking(
            booking_id=instance.id, admin=self.request.user, ip=_client_ip(self.request)
        )


class BookingRuleViewSet(viewsets.ModelViewSet):
    """预约规则(管理员,P3 启用)。"""

    queryset = models.BookingRule.objects.all()
    serializer_class = BookingRuleSerializer
    permission_classes = [IsAdmin]


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """通知:仅本人可见,可标记已读。"""

    serializer_class = NotificationSerializer

    def get_queryset(self):
        return models.Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all read'})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """当前用户未读通知数(前端铃铛 badge 轮询用)。"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """审计日志(管理员只读)。"""

    queryset = models.AuditLog.objects.select_related('user').order_by('-created_at')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['action', 'target_model', 'user']


class StatisticsView(APIView):
    """预约统计(ECharts 友好结构)。"""

    def get(self, request):
        data = models.Book.objects.values('place_name__name').annotate(count=Count('id')).order_by('-count')
        return Response(
            {
                'legend': [d['place_name__name'] for d in data],
                'series': [d['count'] for d in data],
            }
        )
