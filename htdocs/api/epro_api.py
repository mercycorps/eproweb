from django.contrib.auth.models import User

from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from epro.models import Country, Region
from epro.serializers import *


class RViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionReadSerializer


class RWriteViewSet(CreateModelMixin, 
                DestroyModelMixin, 
                UpdateModelMixin, 
                viewsets.GenericViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionWriteSerializer

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionReadSerializer

    def create(self, request):
        serializer = RegionWriteSerializer(data=request.data)
        if serializer.is_valid():
            self.object = serializer.save()
            headers = self.get_success_headers(self.object)
            serializer = RegionReadSerializer(self.object)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, format=None):
        """
        Overriding this method so that it uses RegionWriteSerializer instead of RegionReadSerializer
        """
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = RegionWriteSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountryReadSerializer

    def create(self, request, format=None):
        """
        Overriding this method so that it uses CountryWriteSerializer instead of CountryReadSerializer
        """
        serializer = CountryWriteSerializer(data=request.data)
        if serializer.is_valid():
            self.object = serializer.save()
            headers = self.get_success_headers(serializer.data)
            serializer = CountryReadSerializer(self.object)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Overriding this method so that it uses CountryWriteSerializer instead of CountryReadSerializer
        """
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = CountryWriteSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfficeViewSet(viewsets.ModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeReadSerializer

    def create(self, request, format=None):
        """
        Overriding this method so that it uses CountryWriteSerializer instead of CountryReadSerializer
        """
        serializer = OfficeWriteSerializer(data=request.data)
        if serializer.is_valid():
            self.object = serializer.save()
            headers = self.get_success_headers(serializer.data)
            serializer = OfficeReadSerializer(self.object)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Overriding this method so that it uses CountryWriteSerializer instead of CountryReadSerializer
        """
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = OfficeWriteSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)