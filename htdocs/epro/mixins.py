import json
from django.db.models import F, Q
from django.views.generic import View
from django.http import JsonResponse

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .serializers import FlatJsonSerializer
from .models import Country, Office, UserProfile, Currency, PurchaseRequest
from .forms import PurchaseRequestForm


class LoginRequiredMixin(View):
    """
    Makes a class-based-view require users to authenticate
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """ this is fired up first regardless of what http method is used """
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class AjaxFormResponseMixin(object):
    """
    To add AJAX support to a form; must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxFormResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            response['error'] = True
        return response

    def form_valid(self, form):
        response = super(AjaxFormResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'object': FlatJsonSerializer().serialize([self.object,]),
            }
            return JsonResponse(data)
        else:
            return response

class PurchaseRequestActiveTabMixin(object):
    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestActiveTabMixin, self).get_context_data(**kwargs)
        context['procurement'] = "active_tab"
        return context


class PurchaseRequestMixin(object):
    model = PurchaseRequest
    form_class = PurchaseRequestForm
    context_object_name = 'pr'
    template_name = 'epro/pr_form.html'
    template_name_ajax = 'epro/pr_form_ajax.html'

    """
    Common code between PurchaseRequestCreateView and PurchaseRequestUpdateView is absracted
    into this Mixin
    """

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestMixin, self).get_context_data(**kwargs)
        #html_from_view = OfficeViewSet.as_view({'get': 'list'})(self.request).render().content
        country_id = self.object.country.pk if self.object else self.request.user.userprofile.country.pk
        #serializer = FlatJsonSerializer()
        #context['offices'] = serializer.serialize(Office.objects.filter(country=country_id), fields=('id', 'name'))
        #context['currencies'] = serializer.serialize(Currency.objects.filter(country=country_id), fields=('id', 'code'))

        offices = Office.objects.filter(
            Q(country=country_id)|
            Q(pk=self.object.office.pk if self.object else None)
            ).distinct().annotate(text=F('name')).values('id', 'text')
        context['offices'] = json.dumps(list(offices))

        currencies = Currency.objects.filter(
            Q(country=country_id)|
            Q(pk=self.object.currency.pk if self.object else None)
            ).distinct().annotate(text=F('code')).values('id', 'text')
        context['currencies'] = json.dumps(list(currencies))

        users = UserProfile.objects.filter(
            Q(country_id=country_id)|
            Q(pk=self.object.approver1.pk if self.object else None)|
            Q(pk=self.object.approver2.pk if self.object and self.object.approver2 else None)
            ).distinct().annotate(text=F('name')).values('id', 'text')
        context['users'] = json.dumps(list(users))

        return context

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword arguments."""
        kwargs = super(PurchaseRequestMixin, self).get_form_kwargs()
        kwargs['country_id'] = self.request.user.userprofile.country
        return kwargs

    def form_valid(self, form):
        approverOne = self.request.POST.get('approverOne', None)
        if approverOne:
            approver1= UserProfile.objects.get(pk=approverOne)
            form.instance.approver1 = approver1

        approverTwo = self.request.POST.get('approverTwo', None)
        if approverTwo:
            approver2 = UserProfile.objects.get(pk=approverTwo)
            form.instance.approver2 = approver2

        originating_office = self.request.POST.get('originating_office', None)
        if originating_office:
            office = Office.objects.get(pk=originating_office)
            form.instance.office = office

        pr_currency = self.request.POST.get('pr_currency', None)
        if pr_currency:
            currency = Currency.objects.get(pk=pr_currency)
            form.instance.currency = currency

        return super(PurchaseRequestMixin, self).form_valid(form)

    def get_template_names(self):
        if self.request.is_ajax():
            return [self.template_name_ajax]
        return [self.template_name]

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, project_reference=self.object.project_reference)
