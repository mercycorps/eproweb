from rest_framework import serializers
from rest_framework.response import Response
from django.utils import six
from djangocosign.models import Region, Country, Office
from .models import *


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('name', 'code', 'country', 'created_by', 'updated_by')


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ('name', 'long_name', 'country')


class CountrySerializer(serializers.ModelSerializer):
    offices = OfficeSerializer(many=True)

    class Meta:
        model = Country
        fields = ('iso_two_letters_code', 'name', 'offices', 'region')

    def create(self, validated_data):
        offices_data = validated_data.pop('offices')
        country = Country.object.create(**validated_data)
        for office_data in offices_data:
            Office.objects.create(country=country, **validated_data)
        return country


class RegionSerializer(serializers.ModelSerializer):
    api_url = serializers.SerializerMethodField()
    countries = CountrySerializer(many=True)

    class Meta:
        model = Region
        fields = ('name', 'code', 'countries', 'api_url', 'created_by', 'updated_by')

    def create(self, validated_data):
        countries_data = validated_data.pop('countries')
        region = Region.objects.create(**validated_data)
        for country_data in countries_data:
            Country.objects.create(region=region, **country_data)
        return region

    def get_api_url(self, obj):
        return '#/region/%s/' % obj.id