import json
from django.db.models import F, Q
from django.views.generic import View
from django.http import JsonResponse

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .serializers import FlatJsonSerializer
from .models import Country, Office, UserProfile, Currency

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
            return JsonResponse(form.errors, status=400)
        else:
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


class PurchaseRequestMixin(object):
    """
    Common code between PurchaseRequestCreateView and PurchaseRequestUpdateView is absracted
    into this Mixin
    """
    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestMixin, self).get_context_data(**kwargs)
        if self.object:
            country_id = self.object.country.pk
        else:
            country_id = self.request.user.userprofile.country.pk

        serializer = FlatJsonSerializer()
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

    def form_valid(self, form):
        approverOne = self.request.POST.get('approverOne', None)
        form.instance.approver1 = approverOne

        approverTwo = self.request.POST.get('approverTwo', None)
        form.instance.approver2 = approverTwo

        originating_office = self.request.POST.get('originating_office', None)
        form.instance.office = originating_office

        pr_currency = self.request.POST.get('pr_currency', None)
        form.instance.currency = pr_currency

        return super(PurchaseRequestMixin, self).form_valid(form)