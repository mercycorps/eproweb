from rest_framework import serializers
from rest_framework.response import Response
from django.utils import six
from .models import *

class RegionReadSerializer(serializers.ModelSerializer):
    #countries = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    # StringRelatedField represents relationship's target using its __unicode__ method.
    #countries = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Region
        fields = ('countries', 'code', 'name', 'created_by', 'updated_by')
        #exclude = ('created', 'updated')
        depth = 1


class RegionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region


class CountryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        depth = 1


class CountryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country


class OfficeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        depth = 2


class OfficeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office


class PurchaseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
