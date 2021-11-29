import django_filters
from .models import Box,Profile

class BoxFilter1(django_filters.FilterSet):
    class Meta:
        model = Box
        fields = {
            'length': ['lt', 'gt'],
            'breadth': ['lt', 'gt'],
            'height': ['lt', 'gt'],
            'area': ['lt','gt'],
            'volume': ['lt','gt'],
        }

class BoxFilter2(BoxFilter1):
    BoxFilter1.Meta.fields = {
        'length': ['lt', 'gt'],
        'breadth': ['lt', 'gt'],
        'height': ['lt', 'gt'],
        'area': ['lt','gt'],
        'volume': ['lt','gt'],
        'creator__username': ['exact'],
        'created': ['lt','gt'],
    }