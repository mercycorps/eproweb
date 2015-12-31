from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *


urlpatterns = [
    url(r'^$', FeedbackArchiveIndexView.as_view(), name='feedback_list'),
    url(r'^add/$', FeedbackCreateView.as_view(), name='feedback_add'),
    #url(r'^pr/edit/(?P<pk>\d+)/$', PurchaseRequestUpdateView.as_view(), name='pr_edit'),
    url(r'^(?P<pk>\d+)/$', FeedbackDetailView.as_view(), name='feedback_view'),
    url(r'^filter/$', FeedbackListView.as_view(), name='feedback_filter'),

    url(r'^archive/recent/$', FeedbackArchiveIndexView.as_view(), name='recent'),
    url(r'^archive/monthly/(?P<year>\d{4})/(?P<month>[a-z, A-Z]{3})/$', FeedbackMonthArchiveView.as_view(), name="monthly"),
    url(r'^archive/yearly/(?P<year>\d{4})/$', FeedbackYearArchiveView.as_view(), name="yearly"),

    url(r'^vote/$', FeedbackVotesByUserView.as_view(), name='vote'),

    url(r'^comment/add/$', CommentCreateView.as_view(), name='comment_add'),
]

urlpatterns = format_suffix_patterns(urlpatterns)