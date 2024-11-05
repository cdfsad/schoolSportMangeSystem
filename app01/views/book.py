import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from app01 import models
from app01.utils.pagination import Pagination


def book_admin(request):
    data_dict = {}
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['status__contains'] = search_data
    queryset = models.Book.objects.filter(**data_dict).order_by('date')
    page_obj = Pagination(request, queryset)
    context = {
        'queryset': page_obj.page_queryset,  # 分完页的数据
        'page_string': page_obj.html()  # 页码
    }
    return render(request, 'book_admin.html', context)


def book_agree(request):
    exist = models.Book.objects.filter(id=request.GET.get('bid')).exists()
    if exist:
        obj = models.Book.objects.filter(id=request.GET.get('bid')).first()
        obj.status = 1
        obj.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})


def book_delete(request):
    models.Book.objects.filter(id=request.GET.get('bid')).delete()
    return JsonResponse({'status': True})


def book_delete1(request):
    stu_exist = models.Book.objects.filter(id=request.GET.get('stu_did')).exists()
    if stu_exist:
        models.Book.objects.filter(id=request.GET.get('stu_did')).delete()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})


def book_delete2(request):
    stu_exist = models.Book.objects.filter(id=request.GET.get('admin_did')).exists()
    if stu_exist:
        models.Book.objects.filter(id=request.GET.get('admin_did')).delete()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})


# 预约
def place_book(request, nid, pid):
    html = []
    date = datetime.date.today().strftime('%Y-%m-%d')
    stu_obj = models.Account.objects.filter(id=nid).first()
    place_obj = models.Place.objects.filter(id=pid).first()
    time_list = ['10:00-11:00', '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00',
                 '17:00-18:00', '18:00-19:00', '19:00-20:00', '20:00-21:00']
    date = request.GET.get('time', date)
    exist = models.Book.objects.filter(date=date).exists()
    for t in time_list:
        flag = False
        if exist:
            book_list = models.Book.objects.filter(date=date)
            for book in book_list:
                if book.time == t and book.place_name.pk == pid and book.campus == place_obj.campus:
                    flag = True
                    break
            if flag:
                html.append("<div class='div_style td_save td' id={}></div>".format(t))
            else:
                html.append("<div class='div_style td' id={}></div>".format(t))
        else:
            html.append("<div class='div_style td' id={}></div>".format(t))
    htmls = ''.join(html)
    context = {
        'date': date,
        'list': time_list,
        'place_obj': place_obj,
        'htmls': htmls
    }
    if not stu_obj.auth:
        return render(request, 'book1.html', context)
    return render(request, 'book2.html', context)


# 预约确认
@csrf_exempt
def book_save(request):
    bk_msg_query_dict = request.POST
    b_obj = models.Account.objects.filter(id=request.session["info"]["id"]).first()
    p_obj = models.Place.objects.filter(id=bk_msg_query_dict['place']).first()
    msg_dict = {
        'book_name': b_obj,
        'place_name': p_obj,
        'people': bk_msg_query_dict['people'],
        'date': bk_msg_query_dict['date'],
        'time': bk_msg_query_dict['bkTime'],
        'campus': bk_msg_query_dict['campus'],
    }
    exist = models.Book.objects.filter(place_name=p_obj, time=msg_dict['time'],
                                       date=msg_dict['date']).exists()
    p_max = p_obj.people
    b_peo = msg_dict['people']
    errors_list = ['该时间段已被预订！', '使用人数过多！']
    if exist and int(b_peo) > int(p_max):
        return JsonResponse({'status': False, 'errors': errors_list})
    elif int(b_peo) > int(p_max):
        return JsonResponse({'status': False, 'errors': errors_list[1]})
    elif exist:
        return JsonResponse({'status': False, 'errors': errors_list[0]})
    models.Book.objects.create(**msg_dict)
    return JsonResponse({'status': True})


# 我的预约
def my_book(request):
    stu_id = request.session['info']['id']
    queryset = models.Book.objects.filter(book_name_id=stu_id).all()
    stu_obj = models.Account.objects.filter(id=stu_id).first()
    if stu_obj.auth:
        return render(request, 'my_book2.html', {'queryset': queryset})
    return render(request, 'my_book1.html', {'queryset': queryset})
