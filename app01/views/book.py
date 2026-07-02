"""预约相关视图(调 booking_service,视图层保持薄)。"""

import datetime

from django.http import JsonResponse
from django.shortcuts import redirect, render

from app01 import models
from app01.services import booking_service
from app01.services.booking_service import BookingError
from app01.utils.pagination import Pagination
from app01.utils.permissions import admin_required


@admin_required
def book_admin(request):
    search = request.GET.get('q', '')
    queryset = booking_service.list_all_bookings(search_status=search or None)
    page_obj = Pagination(request, queryset)
    context = {'queryset': page_obj.page_queryset, 'page_string': page_obj.html()}
    return render(request, 'book_admin.html', context)


@admin_required
def book_agree(request):
    approver = models.CustomUser.objects.filter(id=request.session['info']['id']).first()
    booking = booking_service.approve_booking(booking_id=request.POST.get('bid'), approver=approver)
    if booking:
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': '预约不存在'})


@admin_required
def book_delete(request):
    bid = request.POST.get('bid')
    if not bid:
        return JsonResponse({'status': False, 'errors': '缺少参数 bid'})
    ok = booking_service.admin_cancel_booking(booking_id=bid)
    return JsonResponse({'status': ok})


def book_delete1(request):
    # 学生取消自己的预约(归属校验在 service)
    user_id = request.session.get('info', {}).get('id')
    user = models.CustomUser.objects.filter(id=user_id).first()
    ok, msg = booking_service.cancel_booking(booking_id=request.POST.get('stu_did'), user=user)
    if ok:
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': msg})


@admin_required
def book_delete2(request):
    ok = booking_service.admin_cancel_booking(booking_id=request.POST.get('admin_did'))
    if ok:
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': '预约不存在'})


# 预约页面(渲染时段格子)
def place_book(request, pid):
    nid = request.session.get('info', {}).get('id')
    if not nid:
        return redirect('/index/')
    html = []
    date = datetime.date.today().strftime('%Y-%m-%d')
    stu_obj = models.CustomUser.objects.filter(id=nid).first()
    place_obj = models.Place.objects.filter(id=pid).first()
    time_list = [
        '10:00-11:00',
        '13:00-14:00',
        '14:00-15:00',
        '15:00-16:00',
        '16:00-17:00',
        '17:00-18:00',
        '18:00-19:00',
        '19:00-20:00',
        '20:00-21:00',
    ]
    date = request.GET.get('time', date)
    # N+1 修复:一次查询当日该场地该校区所有已预订时段(O(N*M) → 1 次查询)
    booked_times = set(
        models.Book.objects.filter(date=date, place_name_id=pid, campus_id=place_obj.campus_id).values_list(
            'time', flat=True
        )
    )
    for t in time_list:
        cls = 'div_style td_save td' if t in booked_times else 'div_style td'
        html.append("<div class='{}' id={}></div>".format(cls, t))
    htmls = ''.join(html)
    context = {'date': date, 'list': time_list, 'place_obj': place_obj, 'htmls': htmls}
    if stu_obj.role == 'student':
        return render(request, 'book1.html', context)
    return render(request, 'book2.html', context)


# 预约确认(调 booking_service.create_booking,含冲突/容量校验)
def book_save(request):
    user = models.CustomUser.objects.filter(id=request.session["info"]["id"]).first()
    p_obj = models.Place.objects.filter(id=request.POST['place']).first()
    try:
        booking_service.create_booking(
            user=user,
            place=p_obj,
            date=request.POST['date'],
            time_slot=request.POST['bkTime'],
            people=request.POST['people'],
            campus_value=request.POST.get('campus', ''),
        )
    except BookingError as e:
        return JsonResponse({'status': False, 'errors': e.errors})
    return JsonResponse({'status': True})


# 我的预约
def my_book(request):
    user_id = request.session['info']['id']
    user = models.CustomUser.objects.filter(id=user_id).first()
    queryset = booking_service.list_user_bookings(user)
    if user.role == 'student':
        return render(request, 'my_book1.html', {'queryset': queryset})
    return render(request, 'my_book2.html', {'queryset': queryset})
