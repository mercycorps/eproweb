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
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from django.views.generic import TemplateView

from django.contrib import admin

from rest_framework import routers, serializers, viewsets

from .views import HomeView
from api.users_api import *
from epro.api import *

admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'regions', RegionReadViewSet, base_name='regions')
router.register(r'region', RegionWriteViewSet)
router.register(r'countries', CountryReadViewSet, base_name='countries')
router.register(r'country', CountryWriteViewSet)
router.register(r'offices', OfficeReadViewSet, base_name='offices')
router.register(r'office', OfficeWriteViewSet)

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="index.html"), name='home'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^health/$', 'eproweb.views.health_view', name='health'),
    url(r'^home/$', HomeView.as_view(), name='home'),
    url(r'^epro/', include('epro.urls')),
] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
