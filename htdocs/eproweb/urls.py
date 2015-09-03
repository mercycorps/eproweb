"""eproweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers, serializers, viewsets
from api.users_api import *
from api.epro_api import *

admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
#router.register(r'regions', RegionViewSet)
router.register(r'regs', RViewSet, base_name='readonlyregions')
router.register(r'bregsw', RWriteViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'offices', OfficeViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^health/$', 'eproweb.views.health_view', name='health'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^epro/', include('epro.urls')),
]
