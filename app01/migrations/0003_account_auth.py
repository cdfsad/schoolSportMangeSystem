# Generated by Django 4.0.1 on 2022-03-30 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_alter_account_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='auth',
            field=models.SmallIntegerField(choices=[(0, '普通权限'), (1, '管理权限')], default=0, verbose_name='权限'),
        ),
    ]
