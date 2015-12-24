import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers.python import Serializer as PythonSerializer

from rest_framework import serializers
from rest_framework.response import Response
from django.utils import six
from djangocosign.models import Region, Country, Office
from .models import *


class FlatJsonSerializer(PythonSerializer):
    """
    Take a look at the django implementation as a reference if you need further customization:
    https://github.com/django/django/blob/master/django/core/serializers/json.py#L21-62
    Usage:
        serializer = FlatJsonSerializer()
        json_data = serializer.serialize(<queryset>, <optional>fields=('field1', 'field2'))
    """
    def get_dump_object(self, obj):
        data = self._current
        if not self.selected_fields or 'id' in self.selected_fields:
            data['id'] = obj.id
        return data

    def end_object(self, obj):
        if not self.first:
            self.stream.write(', ')
        json.dump(self.get_dump_object(obj), self.stream,
                  cls=DjangoJSONEncoder)
        self._current = None

    def start_serialization(self):
        self.stream.write("[")

    def end_serialization(self):
        self.stream.write("]")

    def getvalue(self):
        return super(PythonSerializer, self).getvalue()


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'name', 'code', 'country', 'created_by', 'updated_by')


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ('id', 'name', 'long_name', 'country')


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