from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from epro.models import Country, Region
from epro.serializers import *


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def pre_save(self, obj):
        obj.created_by = self.request.user
        obj.updated_by = self.request.user


class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer

    def get_queryset(self):
        queryset = Country.objects.all()
        region_id = self.request.query_params.get('region', None)
        if region_id:
            queryset = queryset.filter(region=region_id)
        return queryset

    def pre_save(self, obj):
        obj.created_by = self.request.user
        obj.updated_by = self.request.user


class OfficeViewSet(viewsets.ModelViewSet):
    serializer_class = OfficeSerializer

    def get_queryset(self):
        queryset = Office.objects.all()
        country_id = self.request.query_params.get('country', None)
        if country_id:
            queryset = queryset.filter(country=country_id)
        return queryset

    def pre_save(self, obj):
        obj.created_by = self.request.user
        obj.updated_by = self.request.user


class CurrencyViewSet(viewsets.ModelViewSet):
    serializer_class = CurrencySerializer

    def get_queryset(self):
        queryset = Currency.objects.all()
        country_id = self.request.query_params.get('country', None)
        if country_id:
            queryset = queryset.filter(country=country_id)
        return queryset

    def pre_save(self, obj):
        obj.created_by = self.request.user
        obj.updated_by = self.request.user