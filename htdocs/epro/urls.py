from django.conf.urls import include, url
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import TemplateView

from rest_framework.urlpatterns import format_suffix_patterns

from epro.views import *


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="epro/home.html"), name='eprohome'),
    url(r'^feedback/$', FeedbackCreateView.as_view(), name='feedback'),
    url(r'^newpr/$', PurchaseRequestCreateView.as_view(), name='newpr'),
    url(r'^pr/(?P<pk>\d+)/$', PurchaseRequestDetailView.as_view(), name='pr_detail'),
    url(r'^item/add/(?P<pr>\d+)/$', PurchaseRequestItemCreateView.as_view(), name='item_new'),
    url(r'^item/edit/(?P<pk>\d+)/$', PurchaseRequestItemUpdateView.as_view(), name='item_edit'),
    url(r'^financecodes_new/$', FinanceCodesCreateView.as_view(), name='financecodes_new'),

]

urlpatterns = format_suffix_patterns(urlpatterns)