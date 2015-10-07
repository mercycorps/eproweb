from django.conf.urls import include, url
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import TemplateView

from rest_framework.urlpatterns import format_suffix_patterns

from epro.views import *


urlpatterns = [
    #url(r'^$', PurchaseRequestsList.as_view(), name='pr-list'),
    url(r'^$', TemplateView.as_view(template_name="epro/home.html"), name='home'),
    url(r'^(?P<pk>[0-9]+)/$', PurchaseRequestDetail.as_view(), name='pr-detail'),
    url(r'^regions/$', RegionList.as_view(), name='region-list'),
    url(r'^countries/$', CountryList.as_view(), name='country-list'),
    url(r'^offices/$', OfficeList.as_view(), name='office-list'),
    
]

urlpatterns = format_suffix_patterns(urlpatterns)