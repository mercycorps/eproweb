from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from epro.models import Country, Region
from epro.serializers import *


class RegionReadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionReadSerializer


class RegionWriteViewSet(CreateModelMixin, DestroyModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionWriteSerializer


class CountryReadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountryReadSerializer


class CountryWriteViewSet(CreateModelMixin, DestroyModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Country.objects.all()
    serializer_class = CountryWriteSerializer


class OfficeReadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeReadSerializer


class OfficeWriteViewSet(CreateModelMixin, DestroyModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeWriteSerializer


