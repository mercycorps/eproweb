from django.shortcuts import render

from django.contrib.auth.models import User
from djangocosign.models import UserProfile
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('title', 'name', 'employee_number', 'country', 'user',)

# ViewSets define the view behavior.
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = UserProfile.objects.all()
        emp_number = self.request.query_params.get('employee_number', None)
        if emp_number:
            queryset = queryset.filter(employee_number=emp_number)
        return queryset


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    userprofile = UserProfileSerializer(many=False)
    class Meta:
        model = User
        fields = ('userprofile', 'url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    #queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        email = self.request.query_params.get('email', None)
        if email:
            queryset = queryset.filter(email=email)
        return queryset


