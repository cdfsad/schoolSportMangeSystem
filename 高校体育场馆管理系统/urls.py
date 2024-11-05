"""高校体育场馆管理系统 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app01.views import account, stu, place, book, data


urlpatterns = [
    # path('admin/', admin.site.urls),

    # 首页
    path('index/', account.index),
    # 学生用户登录
    path('login/', account.login),
    # 注册
    path('reg/', account.reg),
    # 注册用户登录
    path('reg_login/', account.reg_login),
    # 注销
    path('logout/', account.logout),
    # 修改密码
    path('account/<int:nid>/reset/', account.change_pwd),
    # 验证码
    path('image/code/', account.image_code),

    # 用户
    path('common/', account.common),
    path('admin/', account.admin),

    # 学生管理
    path('student/list/', stu.stu_list),
    # 上传
    path('student/multi/', stu.stu_multi),
    # 添加保存
    path('student/add/', stu.stu_add),
    # 编辑
    path('student/edit/', stu.stu_edit),
    # 编辑保存
    path('student/edit/save/', stu.stu_edit_save),
    # 删除
    path('student/delete/', stu.stu_delete),

    # 场地管理
    # 东校区
    path('place/list1/', place.place_list1),
    path('place/stu/list1/', place.place_stu_list1),
    # 白云校区
    path('place/list2/', place.place_list2),
    path('place/stu/list2/', place.place_stu_list2),
    # 添加保存
    path('place/add/', place.place_add),
    # 编辑
    path('place/edit/', place.place_edit),
    # 编辑保存
    path('place/edit/save/', place.place_edit_save),
    # 删除
    path('place/delete/', place.place_delete),

    # 预约
    path('place/<int:nid>/<int:pid>/book/', book.place_book),
    # 预约确定
    path('book/save/', book.book_save),
    # 我的预约
    path('my/book/', book.my_book),
    # 取消预约
    path('book/delete1/', book.book_delete1),
    path('book/delete2/', book.book_delete2),
    # 预约管理
    path('book/admin/', book.book_admin),
    # 删除预约
    path('book/delete/', book.book_delete),
    # 审批预约
    path('book/agree/', book.book_agree),

    # 数据统计
    path('data/statistics/', data.data_statistics),
    path('chart/list/', data.chart_list),


]
