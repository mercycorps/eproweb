from django.shortcuts import render

from django.views.generic import TemplateView, FormView, View, DeleteView, CreateView
from django.views.generic.dates import ArchiveIndexView, MonthArchiveView, YearArchiveView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.utils import timezone

from django.contrib.messages.views import SuccessMessageMixin

from .models import Feedback
from .forms import *
from .mixins import FeedbackMixin
from .utils import prepare_query_params


class FeedbackListView(FeedbackMixin, ListView):
    """
    PR List View
    """
    model = Feedback
    template_name = 'feedback/feedback_list.html'
    context_object_name = 'feedback'

    def get_queryset(self):
        kwargs = prepare_query_params(self.request.GET)
        qs = Feedback.objects.filter(**kwargs)
        print(kwargs)
        return qs

class FeedbackCreateView(SuccessMessageMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'feedback/feedback.html'
    success_message = "Thank you for providing feedback."

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        return super(FeedbackCreateView, self).form_valid(form)


class FeedbackDetailView(FeedbackMixin, DetailView):
    model = Feedback
    template_name = "feedback/feedback_detail.html"


class FeedbackArchiveIndexView(FeedbackMixin, ArchiveIndexView):
    """
    A list view showing the "latest" objects, by created date.
    """
    queryset = Feedback.objects.all()
    date_field = "created"
    allow_future = True
    context_object_name = 'feedback'
    template_name = "feedback/feedback_list.html"


class FeedbackYearArchiveView(FeedbackMixin, YearArchiveView):
    """
    Annual View of Feedback entries by created date.
    """
    queryset = Feedback.objects.all()
    date_field = "created"
    make_object_list = True
    allow_future = True
    template_name = "feedback/archive_year.html"
    context_object_name = 'feedback'


class FeedbackMonthArchiveView(FeedbackMixin, MonthArchiveView):
    """
    Monthly view of Feedback entries by created month
    """
    queryset = Feedback.objects.all()
    date_field = "created"
    allow_future = True
    paginate_by=12
    #month_format='%m' # month number
    template_name = "feedback/archive_month.html"
    context_object_name = 'feedback'

