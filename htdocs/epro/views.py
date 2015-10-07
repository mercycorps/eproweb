from django.shortcuts import render
from django.http import Http404
from django.views.generic import TemplateView

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from .serializers import *
from .models import *


class RegionList(generics.ListCreateAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionReadSerializer


class RegionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionReadSerializer


class CountryList(generics.ListCreateAPIView):
    """
    List all countries, or create a new country.
    """
    permission_classes = (IsAuthenticated,)
    
    queryset = Country.objects.all()
    serializer_class = CountryReadSerializer

    def perform_create(self, serializer):
        """
        Called by CreateModelMixin when saving a new object instance.
        """
        serializer.save(created_by=self.request.user, last_updated_by=self.request.user)

    def create(self, request, *args, **kwargs):
        #http://stackoverflow.com/questions/15883678/django-rest-framework-different-depth-for-post-put
        serializer = CountryWriteSerializer(data=request.data)
        if serializer.is_valid():
            self.object = serializer.save()
            headers = self.get_success_headers(serializer.data)
            serializer = CountryReadSerializer(self.object)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#https://thinkster.io/django-angularjs-tutorial/
class CountryDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a country instance.
    """
    queryset = Country.objects.all()
    serializer_class = CountryWriteSerializer

    def perform_update(self, serializer):
        """
        Called by UpdateModelMixin when saving an existing object instance.
        """
        messages.success(self.request._request, 'Success')
        instance = serializer.save(last_updated_by=self.request.user)
        #send_email_confirmation(user=self.request.user, modified=instance)

    def perform_destroy(self, instance):
        """
        Called by DestroyModelMixin when deleting an object instance.
        """
        # Perform a custom pre-delete action.
        # send_deletion_alert(user=instance.created_by, deleted=instance)
        # Delete the object instance.
        instance.delete()

class OfficeList(generics.ListCreateAPIView):
    queryset = Office.objects.all()
    serializer_class = OfficeReadSerializer


class PurchaseRequestsList(generics.ListCreateAPIView):
    """
    List all boards, or create a new board.
    """
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer


class PurchaseRequestsList2(APIView):
    """
    Lists all purchase_requests, or create a new one.
    """
    def get(self, request, format=None):
        purchase_requests = PurchaseRequest.objects.all()
        serializer = PurchaseRequestSerializer(purchase_requests, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = PurchaseRequestSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PurchaseRequestDetail(APIView):
    """
    Retrieve, update or delete a purchase_request instance.
    """
    def get_object(self, pk):
        try:
            return PurchaseRequest.objects.get(pk=pk)
        except PurchaseRequest.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        purchase_request = self.get_object(pk)
        serializer = PurchaseRequestSerializer(purchase_request)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        purchase_request = self.get_object(pk)
        serializer = PurchaseRequestSerializer(purchase_request, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        purchase_request = self.get_object(pk)
        purchase_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
