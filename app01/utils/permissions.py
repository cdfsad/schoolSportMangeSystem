"""
权限控制工具(P0 商业化改造)。

提供轻量 RBAC 装饰器,基于 Account.auth 字段(0=普通用户,1=管理员)。
P1 阶段 Account 继承 AbstractUser 后,可迁移至 Django/DRF 内置权限体系。

设计要点:
- 权限每次从数据库实时读取(不缓存到 session),避免管理员被撤销后权限残留;
- 对 AJAX 请求返回 JSON 403,对普通请求返回 HTML 403;
- 未登录时重定向到首页(中间件通常已拦截,此处为兜底)。
"""

from functools import wraps

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

from app01 import models


def _is_ajax(request):
    """判断是否为 AJAX 请求(用于返回 JSON 而非 HTML 403)。"""
    return request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get(
        'HTTP_ACCEPT', ''
    )


def admin_required(view_func):
    """要求当前登录用户具有管理员权限(auth=1),否则返回 403。"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        info = request.session.get('info')
        if not info or not info.get('id'):
            return redirect('/index/')
        # 实时查询权限,避免 session 残留过期权限
        user = models.CustomUser.objects.filter(id=info['id']).first()
        if not user or user.role != 'admin':
            if _is_ajax(request):
                return JsonResponse(
                    {'status': False, 'errors': {'permission': '无管理员权限'}},
                    status=403,
                )
            return HttpResponse('无权限访问该页面', status=403)
        return view_func(request, *args, **kwargs)

    return wrapper
