from io import BytesIO

from django.shortcuts import HttpResponse, redirect, render

from app01 import models
from app01.services import account_service
from app01.utils.auth_code import check_code
from app01.utils.form import EditPwdForm, LoginForm, RegForm, RegLoginForm
from app01.utils.permissions import admin_required


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
        form = RegLoginForm()
        return render(request, 'reg_login.html', {'form': form})
    form = RegLoginForm(data=request.POST)
    if form.is_valid():
        user_input_code = form.cleaned_data.pop('code')
        # 验证码一次性校验(读取后立即删除,防重放)
        img_code = request.session.pop('img_code', '')
        if user_input_code.upper() != img_code.upper():
            form.add_error('code', '验证码错误')
            return render(request, 'reg_login.html', {'form': form})
        # 按 username 查询(account_service 封装认证逻辑)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = account_service.authenticate(username, password)
        if not user:
            form.add_error('password', '用户名或密码错误')
            return render(request, 'reg_login.html', {'form': form})
        request.session['info'] = {
            'id': user.id,
            'name': user.first_name or user.username,
            'role': user.role,
        }
        request.session.set_expiry(60 * 60 * 24 * 7)
        return render(request, 'student.html')
    return render(request, 'reg_login.html', {'form': form})


def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        user_input_code = form.cleaned_data.pop('code')
        # 验证码一次性校验(读取后立即删除,防重放)
        img_code = request.session.pop('img_code', '')
        if user_input_code.upper() != img_code.upper():
            form.add_error('code', '验证码错误')
            return render(request, 'login.html', {'form': form})
        # 校内登录:学号(id_number)在导入时已写入 username(account_service 认证)
        id_number = form.cleaned_data.get('id_number')
        password = form.cleaned_data.get('password')
        user = account_service.authenticate(id_number, password)
        if not user:
            form.add_error('password', '用户名或密码错误')
            return render(request, 'login.html', {'form': form})
        request.session['info'] = {
            'id': user.id,
            'name': user.first_name or user.username,
            'role': user.role,
        }
        request.session.set_expiry(60 * 60 * 24 * 7)
        if user.role == 'student':
            return redirect('/common/')
        return redirect('/admin/')
    return render(request, 'login.html', {'form': form})


def common(request):
    return render(request, 'student.html')


@admin_required
def admin(request):
    return render(request, 'admin.html')


def logout(request):
    request.session.clear()
    return redirect('/index/')


def image_code(request):
    # 调用 pillow 生成验证码图片
    img, code_string = check_code()
    request.session['img_code'] = code_string
    request.session.set_expiry(60)
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def change_pwd(request):
    # IDOR 修复:用户 ID 从 session 取,而非 URL 参数
    nid = request.session.get('info', {}).get('id')
    if not nid:
        return redirect('/index/')
    row_obj = models.CustomUser.objects.filter(id=nid).first()
    if not row_obj:
        return redirect('/index/')
    title = '修改密码 - {}'.format(row_obj.first_name or row_obj.username)
    if request.method == 'GET':
        form = EditPwdForm(instance=row_obj)
        if row_obj.role == 'student':
            return render(request, 'change1.html', {'form': form, 'title': title})
        return render(request, 'change2.html', {'form': form, 'title': title})
    form = EditPwdForm(data=request.POST, instance=row_obj)
    if form.is_valid():
        form.save()
        # 改密成功后清除 session,强制重新登录
        request.session.flush()
        return redirect('/login/')
    return render(request, 'change1.html', {'form': form, 'title': title})
