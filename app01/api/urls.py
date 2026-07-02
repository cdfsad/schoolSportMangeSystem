"""DRF API 路由(P2a)。挂载在 /api/v1/。"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from app01.api import views

router = DefaultRouter()
router.register('campuses', views.CampusViewSet, basename='campus')
router.register('users', views.CustomUserViewSet, basename='user')
router.register('places', views.PlaceViewSet, basename='place')
router.register('time-slots', views.TimeSlotViewSet, basename='timeslot')
router.register('books', views.BookViewSet, basename='book')
router.register('booking-rules', views.BookingRuleViewSet, basename='bookingrule')
router.register('notifications', views.NotificationViewSet, basename='notification')
router.register('audit-logs', views.AuditLogViewSet, basename='auditlog')

urlpatterns = [
    # Auth
    path('auth/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='token_logout'),
    path('auth/me/', views.MeView.as_view(), name='me'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    # 业务专用端点
    path('users/import/', views.UserImportView.as_view(), name='user_import'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
]
urlpatterns += router.urls
