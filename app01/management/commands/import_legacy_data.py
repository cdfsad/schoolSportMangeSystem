"""
一次性数据导回脚本(P1)。

从 P0 备份的 fixture(backups/p0_snapshot.json)把旧 Account/Place/Book 数据
导入到重构后的新模型(CustomUser/Campus/Place/Book)。

字段映射规则:
- Account.username(姓名) → CustomUser.first_name
- Account.id_number(学号) → CustomUser.username(统一登录名)+ CustomUser.id_number
- Account.password(已是 PBKDF2 哈希) → CustomUser.password(直接拷贝)
- Account.auth(0/1) → CustomUser.role(student/admin)
- Place.campus(字符串) → Campus FK(get_or_create)
- Book 外键 → 通过 id_map 换算到新 PK

幂等:每次运行先清空目标表,可重复执行。
"""

import json

from django.core.management.base import BaseCommand

from app01.models import Book, Campus, CustomUser, Place

# 校区名称 → code 映射
CAMPUS_CODE_MAP = {
    '东校区': 'dong',
    '白云校区': 'baiyun',
    '西校区': 'xi',
    '北校区': 'bei',
}


class Command(BaseCommand):
    help = '从 P0 备份的 fixture 导入历史数据到重构后的新模型'

    def add_arguments(self, parser):
        parser.add_argument('fixture', type=str, help='fixture JSON 文件路径')

    def handle(self, *args, **options):
        fixture_path = options['fixture']
        with open(fixture_path, encoding='utf-8') as f:
            data = json.load(f)

        # 幂等:先清空目标表(防止重复导入产生重复数据)
        Book.objects.all().delete()
        Place.objects.all().delete()
        CustomUser.objects.all().delete()
        Campus.objects.all().delete()

        user_id_map = {}  # 旧 Account.pk → 新 CustomUser.id
        place_id_map = {}  # 旧 Place.pk → 新 Place.id
        campus_cache = {}

        def get_campus(name):
            name = name or '未知校区'
            if name not in campus_cache:
                code = CAMPUS_CODE_MAP.get(name, name)
                campus, _ = Campus.objects.get_or_create(
                    name=name,
                    defaults={'code': code, 'is_active': True},
                )
                campus_cache[name] = campus
            return campus_cache[name]

        # 1. 用户:Account → CustomUser
        for item in data:
            if item['model'] != 'app01.account':
                continue
            f = item['fields']
            role = 'admin' if f.get('auth') == 1 else 'student'
            id_number = f.get('id_number', '') or ''
            # 统一用学号作登录名(username),姓名存 first_name
            username = id_number or f.get('username', '')
            user = CustomUser.objects.create(
                username=username,
                first_name=f.get('username', ''),
                id_number=id_number,
                password=f.get('password', ''),  # 直接拷贝哈希串
                role=role,
            )
            user_id_map[item['pk']] = user.id
            self.stdout.write(f'  用户: username={user.username} first_name={user.first_name} role={role}')

        # 2. 场地:campus 字符串 → Campus FK
        for item in data:
            if item['model'] != 'app01.place':
                continue
            f = item['fields']
            campus = get_campus(f.get('campus', ''))
            place = Place.objects.create(
                name=f.get('name', ''),
                campus=campus,
                people=f.get('people', '0'),
                use=f.get('use', 1),
            )
            place_id_map[item['pk']] = place.id
            self.stdout.write(f'  场地: {place.name} @ {campus.name}')

        # 3. 预约:外键用 id_map 换算
        for item in data:
            if item['model'] != 'app01.book':
                continue
            f = item['fields']
            campus = get_campus(f.get('campus', ''))
            book_name_id = user_id_map.get(f.get('book_name'))
            place_name_id = place_id_map.get(f.get('place_name'))
            if not book_name_id or not place_name_id:
                self.stdout.write(self.style.WARNING(f'  跳过预约 pk={item["pk"]}: 外键映射缺失'))
                continue
            Book.objects.create(
                book_name_id=book_name_id,
                place_name_id=place_name_id,
                campus=campus,
                people=f.get('people', '0'),
                date=f.get('date', ''),
                time=f.get('time', ''),
                status=f.get('status', 0),
            )
            self.stdout.write(f'  预约: user_id={book_name_id} -> place_id={place_name_id}')

        self.stdout.write(
            self.style.SUCCESS(
                f'导入完成: {CustomUser.objects.count()} 用户, '
                f'{Place.objects.count()} 场地, {Book.objects.count()} 预约, '
                f'{Campus.objects.count()} 校区'
            )
        )
