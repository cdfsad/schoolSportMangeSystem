"""场地业务逻辑服务。"""

from app01.models import Place, TimeSlot


def list_places(*, campus_name=None, search=None, only_active=True):
    """场地列表(可按校区/名称过滤)。"""
    qs = Place.objects.all()
    if campus_name:
        qs = qs.filter(campus__name=campus_name)
    if search:
        qs = qs.filter(name__contains=search)
    if only_active:
        qs = qs.filter(use=1)
    return qs.order_by('name')


def list_places_raw(*, campus_name=None, search=None):
    """场地列表(含不可用,管理端用)。"""
    return list_places(campus_name=campus_name, search=search, only_active=False)


def get_place(place_id):
    return Place.objects.filter(id=place_id).first()


def soft_delete_place(place_id):
    """软删除场地。"""
    Place.objects.filter(id=place_id).update(is_deleted=True)


def get_time_slots(campus_id):
    """校区的启用时段。"""
    return TimeSlot.objects.filter(campus_id=campus_id, is_active=True)
