from django.conf.urls import include, url
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import TemplateView

from rest_framework.urlpatterns import format_suffix_patterns

from epro.views import *


urlpatterns = [
    #url(r'^$', PurchaseRequestsList.as_view(), name='pr-list'),
    url(r'^$', TemplateView.as_view(template_name="epro/home.html"), name='home'),
    #url(r'^$', RegionFormView.as_view(), name='home'),
    url(r'^regionform/$', RegionFormView.as_view(), name='prform'),

]

urlpatterns = format_suffix_patterns(urlpatterns)