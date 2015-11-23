from django.shortcuts import render
from django.views.generic import TemplateView, FormView

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets

from .serializers import *
from .models import *
from .forms import *



class PurchaseRequestCreateView(CreateView):
    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = 'epro/new_pr.html'
    context_object_name = 'pr'
    success_message = "%(title)s was created successfully"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, title=self.object.title)

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['itemformset'] = ItemFormset(self.request.POST)
        else:
            context['itemformset'] = ItemFormset()
        context['itemformset_helper'] = ItemFormsetHelper()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        itemformset = context['itemformset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.object.get_absolute_url())  # assuming your model has ``get_absolute_url`` defined.
        else:
            return self.render_to_response(self.get_context_data(form=form))


class RegionFormView(FormView):
    form_class = PurchaseRequestForm
    template_name = 'epro/genericform.html'
    success_url = '/epro/'

    def get_initial(self):
        currencies = Currency.objects.filter(country=self.request.user.userprofile.country.pk)

        init_data = {
            'country': self.request.user.userprofile.country.pk,
            'originator': self.request.user.pk,
            'pr_type': 0, # goods
            'status': 1, # ongoing
            'currency': currencies[0].pk if len(currencies) == 1 else 0,
            }
        return init_data

    def form_valid(self, form):
        return super(RegionFormView, self).form_valid(form)
