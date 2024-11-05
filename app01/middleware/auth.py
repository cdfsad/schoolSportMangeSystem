from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect


from app01 import models


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 如果方法中没有返回值（返回None），继续向后走
        # 如果有返回值，就不能继续
        # 0.排除那些不需要登录就能访问的页面
        # 1.读取当前访问用户的session信息，如果能读到，说明已登陆过，可以继续向后
        info_dict = request.session.get('info')
        list1 = ['/login/', '/reg_login/', '/image/code/', '/index/', '/reg/']
        if request.path_info in list1:
            return
        if info_dict:
            return
        # 2.没有登陆过，回到登录页面
        return redirect('/index/')

    def process_response(self, request, response):
        return response
