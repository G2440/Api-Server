from rest_framework import serializers
from .models import Box,Store
from .utils import A1,V1,L1,L2

class BoxSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = '__all__'

class BoxSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ['length','breadth','height','area','volume']