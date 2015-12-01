from datetime import date

from django.shortcuts import render
from django.views.generic import TemplateView, FormView, View
from django.views.generic.detail import DetailView

from django.utils import timezone

from django.contrib.messages.views import SuccessMessageMixin

from .models import *
from .forms import *
from .mixins import AjaxFormResponseMixin, LoginRequiredMixin


class PurchaseRequestCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    PR Create View
    """
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
    """
    PR Detail View
    """
    model = PurchaseRequest
    template_name = 'epro/pr_detail.html'
    context_object_name = 'pr'

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestDetailView, self).get_context_data(**kwargs)
        context['items'] = Item.objects.filter(purchase_request=self.object.pk)
        context['item_form'] = PurchaseRequestItemForm(initial={
                                    'purchase_request': self.kwargs['pk'],
                                    'form_action': 'item_new',
                                    })
        context['finance_codes_form'] = FinanceCodesForm(initial={'form_action': 'financecodes_new',})
        item_totals = Item.objects.filter(purchase_request=self.object.pk).aggregate(total_usd = Sum('price_estimated_usd_subtotal'), total_local = Sum('price_estimated_local_subtotal'))
        context['total_usd'] = item_totals['total_local']
        context['total_local'] = item_totals['total_usd']
        return context


class PurchaseRequestItemDetailView(DetailView):
    model = Item
    template_name = None
    context_object_name = 'item'


class PurchaseRequestItemCreateView(LoginRequiredMixin, AjaxFormResponseMixin, SuccessMessageMixin, CreateView):
    """
    PR Item Create View
    """
    model = Item
    form_class = PurchaseRequestItemForm
    context_object_name = 'item'
    success_message = "Item, %(description_pr)s created successfully."

    def get_initial(self):
        init_data = { 'form_action': 'item_new', }
        return init_data

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        form.instance.originator = self.request.user.userprofile
        return super(PurchaseRequestItemCreateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, description_pr=self.object.description_pr)

    #def get_success_url(self):
    #    return reverse_lazy('item_detail', kwargs={ "pk": self.object.pk })


class PurchaseRequestItemUpdateView(LoginRequiredMixin, AjaxFormResponseMixin, SuccessMessageMixin, UpdateView):
    """
    PR Item Update View
    """
    model = Item
    form_class = PurchaseRequestItemForm
    context_object_name = 'pr'
    success_message = "Item, %(description_pr)s updated successfully."

    def get_initial(self):
        init_data = { 'form_action': 'item_update', }
        return init_data

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.userprofile
        return super(PurchaseRequestItemUpdateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, description_pr=self.object.description_pr)


class FinanceCodesCreateView(LoginRequiredMixin, AjaxFormResponseMixin, SuccessMessageMixin, CreateView):
    model = FinanceCodes
    form_class = FinanceCodesForm
    context_object_name = 'finance_codes'
    success_message = "Finance Codes, added to PR %(description_pr)s successfully."

    def get_initial(self):
        init_data = { 'form_action': 'financecodes_new', }
        return init_data

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        self.object = form.save()
        item = Item.objects.get(pk=form.cleaned_data['item_id'])
        item.finance_codes.add(self.object)
        return super(FinanceCodesCreateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, description_pr=self.object.fund_code)
