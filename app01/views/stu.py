from django.http import JsonResponse
from django.shortcuts import redirect, render
from openpyxl import load_workbook

from app01 import models
from app01.utils.form import StudentForm
from app01.utils.pagination import Pagination
from app01.utils.permissions import admin_required


# 学生列表
@admin_required
def stu_list(request):
    form = StudentForm()
    data_dict = {}
    search_data = request.GET.get('q', '')
    if search_data:
        # 按姓名(first_name)搜索
        data_dict['first_name__contains'] = search_data
    queryset = models.CustomUser.objects.filter(**data_dict)
    page_obj = Pagination(request, queryset)
    context = {
        'form': form,
        'queryset': page_obj.page_queryset,  # 分完页的数据
        'page_string': page_obj.html(),  # 页码
    }
    return render(request, 'stu_list.html', context)


# 上传
@admin_required
def stu_multi(request):
    """Excel 批量导入学生(含文件安全校验)"""
    file_obj = request.FILES.get('exc')
    if not file_obj:
        return redirect('/student/list/')

    # 文件类型校验(扩展名白名单)
    allowed_exts = ('.xlsx', '.xls')
    if not file_obj.name.lower().endswith(allowed_exts):
        return redirect('/student/list/')

    # 文件大小校验(上限 5MB,防 DoS)
    if file_obj.size > 5 * 1024 * 1024:
        return redirect('/student/list/')

    # 解析 Excel(捕获损坏文件,避免 500 错误)
    try:
        wb = load_workbook(file_obj)
        sheet = wb.worksheets[0]
    except Exception:
        return redirect('/student/list/')

    # 循环获取每一行数据(限制最大行数)
    max_rows = 5000
    for idx, row in enumerate(sheet.iter_rows(min_row=2)):
        if idx >= max_rows:
            break
        id_number = row[0].value
        name = row[1].value
        pwd = row[2].value
        # 跳过空行
        if not id_number or not name or not pwd:
            continue
        id_number = str(id_number)
        if models.CustomUser.objects.filter(id_number=id_number).exists():
            continue
        # 学号作登录名(username),姓名存 first_name
        user = models.CustomUser(
            username=id_number,
            first_name=str(name),
            id_number=id_number,
            role='student',
        )
        user.set_password(str(pwd))
        user.save()
    return redirect('/student/list/')


# 添加
@admin_required
def stu_add(request):
    form = StudentForm(data=request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'errors': form.errors})


# 编辑
@admin_required
def stu_edit(request):
    # 不回填密码(安全);字段适配 CustomUser(first_name/role)
    row_dict = (
        models.CustomUser.objects.filter(id=request.GET.get('uid')).values('first_name', 'id_number', 'role').first()
    )
    context = {'status': True, 'data': row_dict}
    return JsonResponse(context)


# 编辑保存
@admin_required
def stu_edit_save(request):
    row_obj = models.CustomUser.objects.filter(id=request.GET.get('edit_id')).first()
    form = StudentForm(data=request.POST, instance=row_obj)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'errors': form.errors})


# 删除
@admin_required
def stu_delete(request):
    uid = request.POST.get('uid')
    if not uid:
        return JsonResponse({'status': False, 'errors': '缺少参数 uid'})
    models.CustomUser.objects.filter(id=uid).delete()
    return JsonResponse({'status': True})
