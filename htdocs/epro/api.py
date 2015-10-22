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
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def pre_save(self, obj):
        obj.created_by = self.request.user
        obj.updated_by = self.request.user


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def pre_save(self, obj):
        obj.created_by = self.request.user
        obj.updated_by = self.request.user