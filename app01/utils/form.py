from django import forms
from django.core.exceptions import ValidationError

from app01 import models
from app01.utils.bootstrap import BootStrapForm, BootStrapModelForm


class LoginForm(BootStrapForm):
    """校内登录表单(纯 Form):学号 + 密码 + 验证码。

    校内学号在导入/注册时统一写入 username 字段,故登录按 username 查询。
    """

    id_number = forms.CharField(label='学号')
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='验证码')


class RegForm(BootStrapModelForm):
    """校外用户注册。"""

    class Meta:
        model = models.CustomUser
        fields = ['username', 'id_number', 'password']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }
        labels = {
            'username': '用户名',
            'id_number': '手机号',
        }

    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(render_value=True),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if models.CustomUser.objects.filter(username=username).exists():
            raise ValidationError('用户已存在')
        return username

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if models.CustomUser.objects.filter(id_number=id_number).exists():
            raise ValidationError('该手机号已注册')
        return id_number

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm_pwd = self.cleaned_data.get('confirm_password')
        if pwd and pwd != confirm_pwd:
            raise ValidationError('密码不一致')
        return confirm_pwd

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_password(self.cleaned_data['password'])
        instance.role = 'student'
        if commit:
            instance.save()
        return instance


class RegLoginForm(BootStrapForm):
    """校外用户登录表单(纯 Form):用户名 + 密码 + 验证码。"""

    username = forms.CharField(label='用户名')
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='验证码')


class EditPwdForm(BootStrapModelForm):
    """修改密码表单(绑定当前用户 instance)。"""

    old_password = forms.CharField(label='旧密码', widget=forms.PasswordInput(render_value=True))
    new_password = forms.CharField(label='新密码', widget=forms.PasswordInput(render_value=True))
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = models.CustomUser
        fields = []  # old/new/confirm 均为表单字段,不直接渲染 model 字段

    def clean_old_password(self):
        pwd = self.cleaned_data.get('old_password')
        if not self.instance.check_password(pwd):
            raise ValidationError('旧密码错误')
        return pwd

    def clean_new_password(self):
        pwd = self.cleaned_data.get('new_password')
        if pwd and self.instance.check_password(pwd):
            raise ValidationError('新密码与旧密码相同')
        return pwd

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('new_password')
        confirm_pwd = self.cleaned_data.get('confirm_password')
        if pwd and pwd != confirm_pwd:
            raise ValidationError('密码不一致')
        return confirm_pwd

    def save(self, commit=True):
        self.instance.set_password(self.cleaned_data['new_password'])
        if commit:
            self.instance.save()
        return self.instance


class StudentForm(BootStrapModelForm):
    """学生管理表单(管理员 CRUD)。"""

    class Meta:
        model = models.CustomUser
        fields = ['first_name', 'id_number', 'role', 'phone', 'password']
        labels = {
            'first_name': '姓名',
            'id_number': '学号',
        }

    password = forms.CharField(
        label='密 码',
        widget=forms.PasswordInput(render_value=True),
        required=False,
        help_text='编辑时留空表示不修改',
    )

    def clean_password(self):
        # 新建用户时密码必填;编辑时允许留空(保留原密码)
        pwd = self.cleaned_data.get('password')
        if not pwd and not self.instance.pk:
            raise ValidationError('密码不能为空')
        return pwd

    def save(self, commit=True):
        pwd = self.cleaned_data.get('password')
        instance = super().save(commit=False)
        # 学生用学号作登录名(username)
        if not instance.username:
            instance.username = instance.id_number
        if pwd:
            instance.set_password(pwd)
        elif instance.pk:
            # 编辑时密码留空:保留数据库中的原密码,避免被空值覆盖
            original = models.CustomUser.objects.filter(pk=instance.pk).values_list('password', flat=True).first()
            if original:
                instance.password = original
        if commit:
            instance.save()
        return instance


class PlaceForm(BootStrapModelForm):
    """场地表单(campus 为 FK,自动渲染为下拉选择)。"""

    class Meta:
        model = models.Place
        fields = ['name', 'campus', 'people', 'use']
