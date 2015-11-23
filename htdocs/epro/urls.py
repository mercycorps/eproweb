from django.conf.urls import include, url
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import TemplateView

from rest_framework.urlpatterns import format_suffix_patterns

from epro.views import *


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="epro/home.html"), name='eprohome'),
    url(r'^newpr/$', PurchaseRequestCreateView.as_view(), name='newpr'),
    url(r'^regionform/$', RegionFormView.as_view(), name='prform'),

]

urlpatterns = format_suffix_patterns(urlpatterns)