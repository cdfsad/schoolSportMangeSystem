"""P3a: 种子全局默认预约规则(advance_days=7 / daily_limit=1 / cancel_deadline=2h)。"""

from django.db import migrations


def seed_default_rule(apps, schema_editor):
    BookingRule = apps.get_model('app01', 'BookingRule')
    BookingRule.objects.get_or_create(
        place=None,
        place_type='',
        defaults={
            'advance_days': 7,
            'daily_limit_per_user': 1,
            'cancel_deadline_hours': 2,
            'is_active': True,
        },
    )


def remove_default_rule(apps, schema_editor):
    BookingRule = apps.get_model('app01', 'BookingRule')
    BookingRule.objects.filter(place__isnull=True, place_type='').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('app01', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed_default_rule, remove_default_rule),
    ]
