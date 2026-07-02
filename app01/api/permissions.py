"""DRF 自定义权限(P2a)。"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """仅管理员(role='admin')。"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsStaffOrAdmin(BasePermission):
    """工作人员或管理员。"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ('staff', 'admin'))


class IsOwnerOrAdmin(BasePermission):
    """对象级权限:本人或管理员(Book.book_name / Notification.user)。"""

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        owner = getattr(obj, 'book_name', None) or getattr(obj, 'user', None)
        return owner == request.user
