from django.db import models

# Create your models here.


class Account(models.Model):
    username = models.CharField(verbose_name='姓名', max_length=32)
    id_number = models.CharField(verbose_name='证件号', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)
    auth_choice = (
        (0, '普通权限'),
        (1, '管理权限'),
    )
    auth = models.SmallIntegerField(verbose_name='权限', choices=auth_choice, default=0)

    def __str__(self):
        return str(self.username)


class Place(models.Model):
    name = models.CharField(verbose_name='场地', max_length=32)
    people = models.CharField(verbose_name='容纳人数', max_length=32)
    campus = models.CharField(verbose_name='所属校区', max_length=32)
    status_choice = (
        (0, '不可用'),
        (1, '可使用'),
    )
    use = models.SmallIntegerField(verbose_name='状态', choices=status_choice, default=1)

    def __str__(self):
        return str(self.name)


class Book(models.Model):
    book_name = models.ForeignKey(verbose_name='预订人', to='Account', on_delete=models.CASCADE)
    place_name = models.ForeignKey(verbose_name='场地', to='Place', on_delete=models.CASCADE)
    people = models.CharField(verbose_name='使用人数', max_length=32)
    date = models.CharField(verbose_name='日期', max_length=32)
    time = models.CharField(verbose_name='时间段', max_length=32)
    status_choice = (
        (0, '待审批'),
        (1, '已审批'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choice, default=0)
    campus = models.CharField(verbose_name='所属校区', max_length=32)



