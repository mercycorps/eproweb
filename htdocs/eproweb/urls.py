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
router.register(r'users', UserViewSet, base_name='user')
router.register(r'usersprofile', UserProfileViewSet, base_name='usersprofile')
router.register(r'regions', RegionViewSet, base_name='region')
router.register(r'countries', CountryViewSet, base_name='country')
router.register(r'offices', OfficeViewSet, base_name='office')
router.register(r'currencies', CurrencyViewSet, base_name='currency')


urlpatterns = [
    #url(r'^$', TemplateView.as_view(template_name="index.html"), name='home'),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/docs/', include('rest_framework_swagger.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login', kwargs={'template_name': '404.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/'}),
    url(r'^health/$', 'eproweb.views.health_view', name='health'),
    url(r'^epro/', include('epro.urls')),
    url(r'^feedback/', include('feedback.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# https://docs.djangoproject.com/en/1.8/topics/http/views/
# Customizing error views
handler404 = 'eproweb.views.handler404'
handler500 = 'eproweb.views.my_custom_error_view'
#handler403 = 'views.my_custom_permission_denied_view'
#handler400 = 'views.my_custom_bad_request_view'