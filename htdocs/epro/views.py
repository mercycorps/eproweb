from datetime import date

from django.shortcuts import render
from django.views.generic import TemplateView, FormView, View
from django.views.generic.detail import DetailView

from django.utils import timezone

from django.contrib.messages.views import SuccessMessageMixin

from .models import *
from .forms import *
from .mixins import *


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
    context_object_name = 'pr'

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestDetailView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.filter(purchase_request=self.object.pk)
        context['itemform'] = PurchaseRequestItemForm(initial={'purchase_request': self.kwargs['pk']})
        return context

