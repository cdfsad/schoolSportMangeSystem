from django import forms
from django.core.exceptions import ValidationError

from app01 import models
from app01.utils.bootstrap import BootStrapModelForm


class LoginForm(BootStrapModelForm):
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput
    )
    id_number = forms.CharField(
        label='学号',
    )

    class Meta:
        model = models.Account
        exclude = ['username', 'auth']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }


class RegForm(BootStrapModelForm):
    class Meta:
        model = models.Account
        exclude = ['auth']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    username = forms.CharField(
        label='用户名'
    )
    id_number = forms.CharField(
        label='手机号'
    )

    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(render_value=True)
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        exist = models.Account.objects.filter(username=username).first()
        if exist:
            raise ValidationError('用户已存在')
        return username

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm_pwd = self.cleaned_data.get('confirm_password')
        if pwd and pwd != confirm_pwd:
            raise ValidationError('密码不一致')
        return confirm_pwd


class RegLoginForm(BootStrapModelForm):
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput
    )

    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput
    )

    class Meta:
        model = models.Account
        exclude = ['id_number', 'auth']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }


class EditPwdForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(render_value=True)
    )

    old_password = forms.CharField(
        label='旧密码',
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.Account
        fields = ['old_password', 'password', 'confirm_password']
        labels = {
            'password': '新密码'
        }
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    def clean_old_password(self):
        pwd = self.cleaned_data.get('old_password')
        exist = models.Account.objects.filter(password=pwd, id=self.instance.pk).exists()
        if not exist:
            raise ValidationError('旧密码错误')
        return pwd

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        exist = models.Account.objects.filter(password=pwd, id=self.instance.pk).exists()
        if exist:
            raise ValidationError('新密码与旧密码相同')
        return pwd

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm_pwd = self.cleaned_data.get('confirm_password')
        if pwd and pwd != confirm_pwd:
            raise ValidationError('密码不一致')
        return confirm_pwd


class StudentForm(BootStrapModelForm):
    class Meta:
        model = models.Account
        fields = "__all__"

    username = forms.CharField(
        label='姓 名',
        disabled=False,
    )
    id_number = forms.CharField(
        label='学 号',
        disabled=False,
    )
    password = forms.CharField(
        label='密 码',
        widget=forms.PasswordInput(render_value=True),
    )


class PlaceForm(BootStrapModelForm):
    class Meta:
        model = models.Place
        fields = "__all__"






