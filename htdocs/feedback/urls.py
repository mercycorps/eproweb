from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *


urlpatterns = [
    url(r'^$', FeedbackListView.as_view(), name='feedback_ist'),
    url(r'^feedback/add/$', FeedbackCreateView.as_view(), name='feedback_add'),
    #url(r'^pr/edit/(?P<pk>\d+)/$', PurchaseRequestUpdateView.as_view(), name='pr_edit'),
    url(r'^feedback/(?P<pk>\d+)/$', FeedbackDetailView.as_view(), name='feedback_view'),
]

urlpatterns = format_suffix_patterns(urlpatterns)