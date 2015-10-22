from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib import messages

def health_view(request):
    return HttpResponse("Hey, I'm work'n.", content_type="text/plain")

class HomeView(TemplateView):
    template_name='index.html'

    def get(self, request, *args, **kwargs):
        messages.success(self.request, "Hey, I'm Okay.")
        return super(HomeView, self).get(request, *args, **kwargs)


def handler404(request):
    response = render_to_response('404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response