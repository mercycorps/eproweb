from django.http import HttpResponse
from django.views.generic import TemplateView

def health_view(request):
    return HttpResponse("I am Okay.", content_type="text/plain")

class HomeView(TemplateView):
    template_name='index.html'