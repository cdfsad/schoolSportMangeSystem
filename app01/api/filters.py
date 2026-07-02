"""DRF 过滤器(P2a)。"""

import django_filters

from app01.models import Book


class BookFilter(django_filters.FilterSet):
    """预约过滤:状态/场地/校区/日期。"""

    class Meta:
        model = Book
        fields = {
            'status': ['exact'],
            'place_name': ['exact'],
            'campus': ['exact'],
            'date': ['exact'],
            'book_name': ['exact'],
        }
