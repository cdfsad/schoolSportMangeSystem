"""factory_boy 工厂:生成测试数据。"""

import factory

from app01.models import Campus, CustomUser, Place


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'user{n}')
    first_name = '测试用户'
    id_number = factory.Sequence(lambda n: f'idn{n:06d}')
    role = 'student'

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password('Test@12345')
        if create:
            obj.save()


class CampusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campus

    name = factory.Sequence(lambda n: f'校区{n}')
    code = factory.Sequence(lambda n: f'c{n}')


class PlaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Place

    name = factory.Sequence(lambda n: f'场地{n}')
    campus = factory.SubFactory(CampusFactory)
    people = '10'
    use = 1
