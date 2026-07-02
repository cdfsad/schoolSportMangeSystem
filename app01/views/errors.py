"""自定义错误页视图(P2a)。handler404/handler500 在 DEBUG=False 时生效。"""

from django.shortcuts import render


def page_404(request, exception=None):
    return render(request, '404.html', status=404)


def page_500(request):
    return render(request, '500.html', status=500)
