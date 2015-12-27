from datetime import date
import json

from django.db.models import F
from django.shortcuts import render
from django.views.generic import TemplateView, FormView, View, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.utils import timezone

from django.contrib.messages.views import SuccessMessageMixin

from .models import *
from .forms import *
from .mixins import AjaxFormResponseMixin, LoginRequiredMixin, PurchaseRequestMixin
from .serializers import FlatJsonSerializer

class FeedbackCreateView(LoginRequiredMixin, AjaxFormResponseMixin, SuccessMessageMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'epro/feedback.html'
    success_message = "Your request: %(summary)s is sent."

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        return super(FeedbackCreateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, summary=self.object.summary)


class PurchaseRequestCreateView(LoginRequiredMixin, SuccessMessageMixin,
            AjaxFormResponseMixin, PurchaseRequestMixin, CreateView):
    """ PR Create View """
    success_message = "PR for %(project_reference)s created successfully."

    def get_initial(self):
        country_id = self.request.user.userprofile.country.pk
        init_data = {
            'country': country_id,
            'originator': self.request.user.userprofile,
        }
        return init_data

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        form.instance.originator = self.request.user.userprofile
        form.instance.origination_date = date.today()
        return super(PurchaseRequestCreateView, self).form_valid(form)


class PurchaseRequestUpdateView(LoginRequiredMixin, SuccessMessageMixin,
        AjaxFormResponseMixin, PurchaseRequestMixin, UpdateView):
    """ PR Update View """
    success_message = "PR for %(project_reference)s updated successfully."

    def get_initial(self):
        init_data = {
            'country': self.object.country.pk,
            'originating_office': self.object.office.pk,
            'pr_currency': self.object.currency.pk,
            'approverOne': self.object.approver1.pk,
            'approverTwo': self.object.approver2.pk if self.object.approver2 else None,
        }
        return init_data

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.userprofile
        return super(PurchaseRequestUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword arguments."""
        kwargs = super(PurchaseRequestUpdateView, self).get_form_kwargs()
        kwargs['pk'] = self.object.pk
        return kwargs


class PurchaseRequestDetailView(DetailView):
    """ PR Detail View """
    model = PurchaseRequest
    template_name = 'epro/pr_view.html'
    context_object_name = 'pr'

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestDetailView, self).get_context_data(**kwargs)
        item_totals = Item.objects.filter(purchase_request=self.object.pk).aggregate(total_usd = Sum('price_estimated_usd_subtotal'), total_local = Sum('price_estimated_local_subtotal'))
        context['total_local'] = item_totals['total_local']
        context['total_usd'] = item_totals['total_usd']
        return context


class PurchaseRequestListView(ListView):
    """
    PR List View
    """
    model = PurchaseRequest
    template_name = 'epro/pr_list.html'
    context_object_name = 'prs'


class PurchaseRequestItemCreateView(LoginRequiredMixin, SuccessMessageMixin, AjaxFormResponseMixin, CreateView):
    """
    PR Item Create View
    """
    model = Item
    form_class = PurchaseRequestItemForm
    context_object_name = 'item'
    success_message = "Item created successfully; now, add finance code allocations."

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        form.instance.originator = self.request.user.userprofile
        self.object = form.save()

        try:
            finance_codes = FinanceCodes.objects.get(items__purchase_request__pk=self.object.purchase_request.id, default_for_new_items=True)
            finance_codes.pk = None
            finance_codes.default_for_new_items = False
            finance_codes.save()
            self.object.finance_codes.add(finance_codes)
        except FinanceCodes.DoesNotExist as e:
            print("there is no default finance codes for this PR to be used for new items")
        except FinanceCodes.MultipleObjectsReturned as e:
            print("this should never happen")
        return super(PurchaseRequestItemCreateView, self).form_valid(form)

    def get_initial(self):
        """
        For seting up the form_action in the ItemForm AS WELL AS providing initial value
        to purchase_request field in the Item Form!!!
        """
        return {'purchase_request': self.kwargs.get('pr', None)}

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestItemCreateView, self).get_context_data(**kwargs)
        context['finance_codes_form'] = FinanceCodesForm(initial={'form_action': 'financecodes_new', 'item_id': 0})
        return context


class PurchaseRequestItemUpdateView(LoginRequiredMixin, SuccessMessageMixin, AjaxFormResponseMixin, UpdateView):
    """
    PR Item Update View
    """
    model = Item
    form_class = PurchaseRequestItemForm
    context_object_name = 'item'
    success_message = "Item updated successfully."

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword arguments."""
        kwargs = super(PurchaseRequestItemUpdateView, self).get_form_kwargs()
        kwargs['pk'] = self.object.pk
        return kwargs

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.userprofile
        return super(PurchaseRequestItemUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestItemUpdateView, self).get_context_data(**kwargs)
        context['finance_codes_form'] = FinanceCodesForm(initial={
            'form_action': 'financecodes_new',
            'item_id': self.object.pk,
        })
        return context


class FinanceCodesCreateView(LoginRequiredMixin, SuccessMessageMixin, AjaxFormResponseMixin, CreateView):
    """ This form is always submitted via AJAX """
    model = FinanceCodes
    form_class = FinanceCodesForm
    context_object_name = 'finance_codes'
    success_message = "Finance Codes, added to PR %(description_pr)s successfully."

    def get_initial(self):
        return { 'form_action': 'financecodes_new', 'item_id': self.kwargs['item_id']}

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        self.object = form.save()
        item = Item.objects.get(pk=form.cleaned_data['item_id'])
        item.finance_codes.add(self.object)
        return super(FinanceCodesCreateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, description_pr=self.object.fund_code)


class FinanceCodesUpdateView(LoginRequiredMixin, SuccessMessageMixin, AjaxFormResponseMixin, UpdateView):
    """ This form is always submitted via AJAX """
    model = FinanceCodes
    form_class = FinanceCodesForm
    context_object_name = 'finance_codes'
    success_message = "Finance Codes, updated %(fundcode)s successfully."

    def get_initial(self):
        return { 'form_action': 'financecodes_edit', 'pk': self.object.pk, }

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.userprofile
        return super(FinanceCodesUpdateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, fundcode=self.object.fund_code)


class FinanceCodesDeleteView(LoginRequiredMixin, SuccessMessageMixin, AjaxFormResponseMixin, DeleteView):
    model = FinanceCodes
