from rest_framework import serializers
from rest_framework.response import Response
from django.utils import six
from .models import *


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('name', 'code', 'country', 'created_by', 'updated_by')


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('iso2', 'name', 'region', 'created_by', 'updated_by')
        #depth = 1


class RegionSerializer(serializers.ModelSerializer):
    countries = CountrySerializer(many=True)

    class Meta:
        model = Region
        fields = ('name', 'code', 'countries', 'created_by', 'updated_by')

    def create(self, validated_data):
        countries_data = validated_data.pop('countries')
        region = Region.objects.creaet(**validated_data)
        for country_data in countries_data:
            Country.objects.create(region=region, **country_data)
        return region
