from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from app01 import models
from app01.utils.pagination import Pagination
from app01.utils.form import PlaceForm


# 东校区场地
def place_list1(request):
    form = PlaceForm()
    data_dict = {'campus': '东校区'}
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['name__contains'] = search_data
    queryset = models.Place.objects.filter(**data_dict).order_by('name')
    page_obj = Pagination(request, queryset)
    context = {
        'form': form,
        'queryset': page_obj.page_queryset,  # 分完页的数据
        'page_string': page_obj.html()  # 页码
    }
    return render(request, 'place_list.html', context)


def place_stu_list1(request):
    form = PlaceForm()
    data_dict = {'campus': '东校区'}
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['name__contains'] = search_data
    queryset = models.Place.objects.filter(**data_dict).order_by('name')
    page_obj = Pagination(request, queryset)
    context = {
        'form': form,
        'queryset': page_obj.page_queryset,  # 分完页的数据
        'page_string': page_obj.html()  # 页码
    }
    return render(request, 'place_stu_list.html', context)


# 白云校区场地
def place_list2(request):
    form = PlaceForm()
    data_dict = {'campus': '白云校区'}
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['name__contains'] = search_data
    queryset = models.Place.objects.filter(**data_dict).order_by('name')
    page_obj = Pagination(request, queryset)
    context = {
        'form': form,
        'queryset': page_obj.page_queryset,  # 分完页的数据
        'page_string': page_obj.html()  # 页码
    }
    return render(request, 'place_list.html', context)


def place_stu_list2(request):
    form = PlaceForm()
    data_dict = {'campus': '白云校区'}
    search_data = request.GET.get('q', '')
    if search_data:
        data_dict['name__contains'] = search_data
    queryset = models.Place.objects.filter(**data_dict).order_by('name')
    page_obj = Pagination(request, queryset)
    context = {
        'form': form,
        'queryset': page_obj.page_queryset,  # 分完页的数据
        'page_string': page_obj.html()  # 页码
    }
    return render(request, 'place_stu_list.html', context)


# 添加保存
@csrf_exempt
def place_add(request):
    form = PlaceForm(data=request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'errors': form.errors})


# 编辑
def place_edit(request):
    row_dict = models.Place.objects.filter(id=request.GET.get('pid')).values('name', 'people',
                                                                             'campus', 'use').first()
    context = {
        'status': True,
        'data': row_dict
    }
    return JsonResponse(context)


# 编辑保存
@csrf_exempt
def place_edit_save(request):
    row_obj = models.Place.objects.filter(id=request.GET.get('edit_id')).first()
    form = PlaceForm(data=request.POST, instance=row_obj)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'errors': form.errors})


# 删除
def place_delete(request):
    models.Place.objects.filter(id=request.GET.get('pid')).delete()
    return JsonResponse({'status': True})




