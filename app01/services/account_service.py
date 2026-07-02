"""账户业务逻辑服务。"""

from openpyxl import load_workbook

from app01.models import CustomUser


def authenticate(username, password):
    """按 username 查询并校验密码。返回 user 或 None。"""
    user = CustomUser.objects.filter(username=username).first()
    if user and user.check_password(password):
        return user
    return None


def register_outside_user(*, username, id_number, password):
    """注册校外用户。返回 (user, error_msg)。"""
    if CustomUser.objects.filter(username=username).exists():
        return None, '用户已存在'
    if CustomUser.objects.filter(id_number=id_number).exists():
        return None, '该手机号已注册'
    user = CustomUser(username=username, id_number=id_number, role='student')
    user.set_password(password)
    user.save()
    return user, None


def change_password(*, user, old_password, new_password):
    """修改密码(校验旧密码)。返回 (ok, error_msg)。"""
    if not user.check_password(old_password):
        return False, '旧密码错误'
    if user.check_password(new_password):
        return False, '新密码与旧密码相同'
    user.set_password(new_password)
    user.save()
    return True, None


def import_students_from_excel(file_obj, max_rows=5000):
    """Excel 批量导入学生。

    返回 {'success': n, 'skipped': m, 'error': str|None}。
    """
    try:
        wb = load_workbook(file_obj)
        sheet = wb.worksheets[0]
    except Exception:
        return {'success': 0, 'skipped': 0, 'error': '文件解析失败'}

    success = 0
    skipped = 0
    for idx, row in enumerate(sheet.iter_rows(min_row=2)):
        if idx >= max_rows:
            break
        id_number = row[0].value
        name = row[1].value
        pwd = row[2].value
        if not id_number or not name or not pwd:
            continue
        id_number = str(id_number)
        if CustomUser.objects.filter(id_number=id_number).exists():
            skipped += 1
            continue
        user = CustomUser(
            username=id_number,  # 学号作登录名
            first_name=str(name),
            id_number=id_number,
            role='student',
        )
        user.set_password(str(pwd))
        user.save()
        success += 1
    return {'success': success, 'skipped': skipped, 'error': None}


def list_students(search=None):
    """学生列表(可按姓名搜索)。"""
    qs = CustomUser.objects.all()
    if search:
        qs = qs.filter(first_name__contains=search)
    return qs
