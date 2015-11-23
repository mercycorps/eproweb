from django.shortcuts import render
from django.views.generic import TemplateView, FormView

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets

from .serializers import *
from .models import *
from .forms import *


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
