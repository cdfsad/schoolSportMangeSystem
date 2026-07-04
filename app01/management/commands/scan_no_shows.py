"""扫描违约预约的管理命令(P3b)。

用法:
    python manage.py scan_no_shows              # 默认 30 分钟宽限
    python manage.py scan_no_shows --grace 0    # 立即标记所有已过期

dev/定时:直接调任务函数(同步),免 celery worker;
prod:celery-beat 每 30 分钟自动触发 app01.tasks.scan_no_shows。
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '扫描已过开始时间 + 宽限期的已通过预约,标记为违约(status=5)并通知预订人'

    def add_arguments(self, parser):
        parser.add_argument(
            '--grace',
            type=int,
            default=30,
            help='宽限分钟数(预约开始后多久未签到算违约,默认 30)',
        )

    def handle(self, *args, **options):
        from app01.tasks import scan_no_shows

        grace = options['grace']
        count = scan_no_shows(grace_minutes=grace)
        self.stdout.write(self.style.SUCCESS(f'扫描完成:标记 {count} 条违约预约(宽限 {grace} 分钟)'))
