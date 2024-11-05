from app01 import models
from django.http import JsonResponse
from django.shortcuts import render


def data_statistics(request):
    c1 = models.Book.objects.filter(place_name__name__contains="篮球").count()
    c2 = models.Book.objects.filter(place_name__name__contains="排球").count()
    c3 = models.Book.objects.filter(place_name__name__contains="网球").count()
    c4 = models.Book.objects.filter(place_name__name__contains="乒乓球").count()
    c5 = models.Book.objects.filter(place_name__name__contains="羽毛球").count()
    legend = ['预约情况']
    x_axis = ['篮球', '排球', '网球', '乒乓球', '羽毛球']
    series = [
        {
            'name': '预约情况',
            'type': 'bar',
            'data': [c1, c2, c3, c4, c5]
        }
    ]
    result = {
        'status': True,
        'data': {
            'legend': legend,
            'x_axis': x_axis,
            'series': series,
        }
    }
    return JsonResponse(result)


def chart_list(request):
    return render(request, 'chart_list.html')
