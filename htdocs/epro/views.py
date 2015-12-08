from datetime import date

from django.shortcuts import render
from django.views.generic import TemplateView, FormView, View
from django.views.generic.detail import DetailView

from django.utils import timezone

from django.contrib.messages.views import SuccessMessageMixin

from .models import *
from .forms import *
from .mixins import AjaxFormResponseMixin, LoginRequiredMixin


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


class PurchaseRequestCreateView(LoginRequiredMixin, SuccessMessageMixin, AjaxFormResponseMixin, CreateView):
    """ PR Create View """
    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = 'epro/pr_form.html'
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


class PurchaseRequestUpdateView(LoginRequiredMixin, AjaxFormResponseMixin, UpdateView):
    """ PR Update View """
    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = 'epro/pr_form2.html'
    context_object_name = 'pr'
    #success_message = "PR for %(project_reference)s updated successfully."

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.userprofile
        return super(PurchaseRequestUpdateView, self).form_valid(form)

    #def get_success_message(self, cleaned_data):
    #    return self.success_message % dict(cleaned_data, project_reference=self.object.project_reference)


class PurchaseRequestDetailView(DetailView):
    """
    PR Detail View
    """
    model = PurchaseRequest
    template_name = 'epro/pr_view.html'
    context_object_name = 'pr'

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestDetailView, self).get_context_data(**kwargs)
        item_totals = Item.objects.filter(purchase_request=self.object.pk).aggregate(total_usd = Sum('price_estimated_usd_subtotal'), total_local = Sum('price_estimated_local_subtotal'))
        context['total_usd'] = item_totals['total_local']
        context['total_local'] = item_totals['total_usd']
        return context


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
        return super(PurchaseRequestItemCreateView, self).form_valid(form)

    def get_initial(self):
        """
        For seting up the form_action in the ItemForm as well as providing initial value
        to purchase_request field in the Item Form.
        """
        return {'purchase_request': self.kwargs.get('pr', None)}

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestItemCreateView, self).get_context_data(**kwargs)
        context['finance_codes_form'] = FinanceCodesForm(initial={'form_action': 'financecodes_new',})
        return context


class PurchaseRequestItemUpdateView(LoginRequiredMixin, SuccessMessageMixin, AjaxFormResponseMixin, UpdateView):
    """
    PR Item Update View
    """
    model = Item
    form_class = PurchaseRequestItemForm
    context_object_name = 'item'
    success_message = "Item updated successfully."

    def get_initial(self):
        """ Used in the ItemForm to set the form_action """
        return {'pk': self.object.pk}

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
        return { 'form_action': 'financecodes_new', }

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
        return { 'form_action': 'financecodes_update', 'pk': self.object.pk, }

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.userprofile
        return super(FinanceCodesUpdateView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, fundcode=self.object.fund_code)

