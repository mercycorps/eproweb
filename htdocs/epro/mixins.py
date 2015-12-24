import json
from django.db.models import F
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
        country_id = self.request.user.userprofile.country.pk

        # By default, limit office and currency dropdowns to  the user's country
        serializer = FlatJsonSerializer()
        #context['offices'] = serializer.serialize(Office.objects.filter(country=country_id), fields=('id', 'name'))
        #context['currencies'] = serializer.serialize(Currency.objects.filter(country=country_id), fields=('id', 'code'))
        offices = Office.objects.filter(country=country_id).annotate(text=F('name')).values('id', 'text')
        context['offices'] = json.dumps(list(offices))
        currencies = Currency.objects.filter(country=country_id).annotate(text=F('code')).values('id', 'text')
        context['currencies'] = json.dumps(list(currencies))
        users = UserProfile.objects.filter(country=country_id).annotate(text=F('name')).values('id', 'text')
        context['users'] = json.dumps(list(users))
        return context

    def form_valid(self, form):
        print(self.request.POST.get('approver', "no approver"))
        print("form_valid in MIXIN")
        return super(PurchaseRequestMixin, self).form_valid(form)