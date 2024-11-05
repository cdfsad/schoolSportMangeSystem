from io import BytesIO

from django.shortcuts import render, redirect, HttpResponse
from app01 import models
from app01.utils.form import LoginForm, EditPwdForm, RegForm, RegLoginForm

from app01.utils.auth_code import check_code


def index(request):
    return render(request, 'home.html')


def reg(request):
    if request.method == 'GET':
        reg_form = RegForm()
        return render(request, 'reg.html', {'form': reg_form})

    reg_form = RegForm(data=request.POST)
    if reg_form.is_valid():
        reg_form.save()
        return redirect('/reg_login/')
    return render(request, 'reg.html', {'form': reg_form})


def reg_login(request):
    if request.method == 'GET':
        reg_login_form = RegLoginForm()
        return render(request, 'reg_login.html', {'form': reg_login_form})
    reg_login_form = RegLoginForm(data=request.POST)
    if reg_login_form.is_valid():
        user_input_code = reg_login_form.cleaned_data.pop('code')
        img_code = request.session.get('img_code', '')
        if user_input_code.upper() != img_code.upper():
            reg_login_form.add_error('code', '验证码错误')
            return render(request, 'reg_login.html', {'form': reg_login_form})
        obj = models.Account.objects.filter(**reg_login_form.cleaned_data).first()
        if not obj:
            reg_login_form.add_error('password', '用户名或密码错误')
            return render(request, 'reg_login.html', {'form': reg_login_form})
        request.session['info'] = {'id': obj.id, 'name': obj.username}
        request.session.set_expiry(60 * 60 * 24 * 7)
        return render(request, 'student.html')
    return render(request, 'reg_login.html', {'form': reg_login_form})


def login(request):
    if request.method == 'GET':
        login_form = LoginForm()
        return render(request, 'login.html', {'form': login_form})

    login_form = LoginForm(data=request.POST)
    if login_form.is_valid():
        # 验证成功，获取到证件号、密码、输入的验证码
        # 验证码的校验
        user_input_code = login_form.cleaned_data.pop('code')
        img_code = request.session.get('img_code', '')
        if user_input_code.upper() != img_code.upper():
            login_form.add_error('code', '验证码错误')
            return render(request, 'login.html', {'form': login_form})
        # 去数据库校验用户名和密码是否正确，获取用户对象，None
        obj = models.Account.objects.filter(**login_form.cleaned_data).first()
        if not obj:
            login_form.add_error('password', '用户名或密码错误')
            return render(request, 'login.html', {'form': login_form})
        # 用户名和密码正确
        # 网站生成随机字符串，写到用户浏览器的cookie中;再写入到session中
        request.session['info'] = {'id': obj.id, 'name': obj.username}
        request.session.set_expiry(60 * 60 * 24 * 7)
        if not obj.auth:
            return redirect('/common/')
        return redirect('/admin/')
    return render(request, 'login.html', {'form': login_form})


def common(request):
    return render(request, 'student.html')


def admin(request):
    return render(request, 'admin.html')


def logout(request):
    request.session.clear()
    return redirect('/index/')


def image_code(request):
    # 调用pillow函数，生成图片
    img, code_string = check_code()
    # 写入到自己的session中，以便后续获取验证码再进行校验
    request.session['img_code'] = code_string
    # 给session设置60s超时
    request.session.set_expiry(60)
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def change_pwd(request, nid):
    row_obj = models.Account.objects.filter(id=nid).first()
    title = '修改密码 - {}'.format(row_obj.username)
    if request.method == 'GET':
        form = EditPwdForm()
        if not row_obj.auth:
            return render(request, 'change1.html', {'form': form, 'title': title})
        return render(request, 'change2.html', {'form': form, 'title': title})
    form = EditPwdForm(data=request.POST, instance=row_obj)
    if form.is_valid():
        form.save()
        return redirect('/login/')
    return render(request, 'change1.html', {'form': form, 'title': title})
