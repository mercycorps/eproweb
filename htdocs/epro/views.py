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
    form_class = RegionForm
    template_name = 'epro/genericform.html'
    success_url = '/epro/'

    def form_valid(self, form):
        return super(RegionFormView, self).form_valid(form)
