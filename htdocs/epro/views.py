from datetime import date

from django.shortcuts import render
from django.views.generic import TemplateView, FormView, View
from django.views.generic.detail import DetailView

from django.utils.decorators import method_decorator
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin

from .serializers import *
from .models import *
from .forms import *


class LoginRequiredMixin(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """ this is fired up first regardless of what http method is used """
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class PurchaseRequestCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = 'epro/new_pr.html'
    context_object_name = 'pr'
    success_message = "PR for %(project_reference)s created successfully. You may not add items and submit it."

    def get_initial(self):
        init_data = {
            'country': self.request.user.userprofile.country,
            'originator': self.request.user.userprofile,
        }
        return init_data

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        form.instance.originator = self.request.user.userprofile
        form.instance.origination_date = date.today()
        form.pr_type = PurchaseRequest.TYPE_GOODS
        form.status = PurchaseRequest.STATUS_ONGOING
        return super(PurchaseRequestCreateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, project_reference=self.object.project_reference)


class PurchaseRequestDetailView(DetailView):
    model = PurchaseRequest
    template_name = 'epro/pr_detail.html'

