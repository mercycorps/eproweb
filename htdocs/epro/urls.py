from django.conf.urls import include, url
from django.views.decorators.csrf import csrf_exempt
from epro.views import *

urlpatterns = [
    url(r'^regions/$', RegionList.as_view(), name='region_list'),
    url(r'^countries/$', CountryList.as_view(), name='country_list'),
    url(r'^offices/$', OfficeList.as_view(), name='office_list'),
    url(r'^prs/$', PurchaseRequestsList.as_view(), name='pr_list'),
]