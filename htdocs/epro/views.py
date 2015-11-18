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
        print(self.request.user)
        init_data = {
            'country': 1,
            'originator': self.request.user.pk,
            }
        return init_data

    def form_valid(self, form):
        return super(RegionFormView, self).form_valid(form)
