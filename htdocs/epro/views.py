from datetime import date
import json

from django.db.models import F
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView, View, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.core.exceptions import PermissionDenied

from django.utils import timezone

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .models import *
from .forms import *
from .mixins import AjaxFormResponseMixin, LoginRequiredMixin, PurchaseRequestMixin, PurchaseRequestActiveTabMixin
from .serializers import FlatJsonSerializer


class PurchaseRequestCreateView(LoginRequiredMixin, SuccessMessageMixin,
            AjaxFormResponseMixin, PurchaseRequestActiveTabMixin, PurchaseRequestMixin, CreateView):
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
        AjaxFormResponseMixin, PurchaseRequestActiveTabMixin, PurchaseRequestMixin, UpdateView):
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


class PurchaseRequestDetailView(PurchaseRequestActiveTabMixin, DetailView):
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


class PurchaseRequestListView(PurchaseRequestActiveTabMixin, ListView):
    """
    PR List View
    """
    model = PurchaseRequest
    template_name = 'epro/pr_list.html'
    context_object_name = 'prs'


class ApplyDefaultFinanceCodesToAllItems(LoginRequiredMixin, View):
    """
    Applies the default Finance Codes, if set for an item in this PR, to all items in this PR
    """
    def post(self, request, *args, **kwargs):
        pr_id = kwargs.get('pr_id', None)
        if pr_id is not None:
            try:
                item_with_default_codes = Item.objects.get(purchase_request=pr_id, default_finance_codes=True)
                default_finance_codes = item_with_default_codes.finance_codes.all()
                items = Item.objects.filter(purchase_request=pr_id, default_finance_codes=False)
                for item in items:
                    # delete existing finance codes from each item
                    item.finance_codes.all().delete()
                    # add finance codes from the item that has the default_finance_codes attribute set to True
                    for code in default_finance_codes:
                        code.item = item
                        code.pk = None
                        code.save()
            except Item.DoesNotExist as e:
                messages.error(request, "There is no item with default finance codes set in this PR (%s)" % pr_id)
            except Item.MultipleObjectsReturned as e:
                messages.error(request, "There are multiple items with default finance codes in this PR (%s)" % pr_id)
            messages.success(request, "Successfully set default finance codes for all items.")
        return JsonResponse({"status": "completed"})


class SetDefaultFinanceCodesForPR(LoginRequiredMixin, View):
    """
    Clears any existing default finance codes for a PR and adds new one
    """
    success_message = "Default Finance Codes Set for this Purchase Reqeuest."

    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id', None)

        if item_id is not None:
            item = Item.objects.get(pk=item_id)
            pr = item.purchase_request
            try:
                existing_item_with_default = Item.objects.get(purchase_request=pr.pk, default_finance_codes=True)
                existing_item_with_default.default_finance_codes = False
                existing_item_with_default.save()
            except Item.DoesNotExist as e:
                pass
            except Item.MultipleObjectsReturned as e:
                items = Item.objects.filter(purchase_request=pr.pk, default_finance_codes=True)
                for i in items:
                    i.default_finance_codes = False
                    i.save()

            item.default_finance_codes = True
            item.save()
            messages.success(request, "Successfully set default Finance Codes for PR # %s-%s" % (pr.office.name, pr.sno))
        else:
            messages.error(request, "Could not find the any item to set its finance codes as default.")
        return JsonResponse({"status": "completed"})


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
            default_finance_codes = Item.objects.get(purchase_request=self.object.purchase_request.pk, default_finance_codes=True).finance_codes.all()
            for code in default_finance_codes:
                code.item = self.object
                code.pk= None
                code.save()
        except Item.DoesNotExist as e:
            print("there is no default finance codes for this PR to be used for new items")
        except Item.MultipleObjectsReturned as e:
            print("there should never be more than one default set of finance codes a RP")
        return super(PurchaseRequestItemCreateView, self).form_valid(form)

    def get_initial(self):
        """
        For seting up the form_action in the ItemForm AS WELL AS providing initial value
        to purchase_request field in the Item Form!!!
        """
        return {'purchase_request': self.kwargs.get('pr', None)}

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestItemCreateView, self).get_context_data(**kwargs)
        context['finance_codes_form'] = FinanceCodesForm(initial={'item': 0})
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
        context['finance_codes_form'] = FinanceCodesForm(initial={'item': self.object.pk})
        return context


class PurchaseRequestItemDeleteView(LoginRequiredMixin, DeleteView):
    """
    Deletes an Item in a Purchase Request
    """
    model = Item
    success_message = "Item was deleted successfully."
    object = None
    pr_totals = None

    def get_success_url(self):
        return reverse_lazy('pr_view', kwargs={'pk': self.object.purchase_request.id})

    def get_object(self, queryset=None):
        #Hook to ensure object is owned by request.user.
        self.object = super(PurchaseRequestItemDeleteView, self).get_object()
        if not self.object.created_by == self.request.user.userprofile:
            raise PermissionDenied
        return self.object

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.success_message)
        super(PurchaseRequestItemDeleteView, self).delete(request, *args, **kwargs)
        self.pr_totals = Item.objects.filter(purchase_request=self.object.purchase_request.pk).aggregate(total_usd = Sum('price_estimated_usd_subtotal'), total_local = Sum('price_estimated_local_subtotal'))
        return JsonResponse({"total_usd": self.pr_totals["total_usd"], "total_local": self.pr_totals["total_local"]})


class FinanceCodesCreateView(SuccessMessageMixin, AjaxFormResponseMixin, CreateView):
    """ This form is always submitted via AJAX """
    model = FinanceCodes
    form_class = FinanceCodesForm
    context_object_name = 'finance_codes'
    success_message = "Finance Codes, added to PR %(description_pr)s successfully."

    def get_initial(self):
        initial = {'item': self.kwargs.get('item_id', None)}
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        #self.object = form.save()
        return super(FinanceCodesCreateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, description_pr=self.object.fund_code)


class FinanceCodesUpdateView(LoginRequiredMixin, SuccessMessageMixin, AjaxFormResponseMixin, UpdateView):
    """ This form is always submitted via AJAX """
    model = FinanceCodes
    form_class = FinanceCodesForm
    context_object_name = 'finance_codes'
    success_message = "Finance Codes, updated %(fundcode)s successfully."

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword arguments."""
        kwargs = super(FinanceCodesUpdateView, self).get_form_kwargs()
        kwargs['pk'] = self.object.pk
        return kwargs

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.userprofile
        return super(FinanceCodesUpdateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, fundcode=self.object.fund_code)


class FinanceCodesDeleteView(LoginRequiredMixin, SuccessMessageMixin, AjaxFormResponseMixin, DeleteView):
    model = FinanceCodes
