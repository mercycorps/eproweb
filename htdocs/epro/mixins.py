from django.views.generic import View
from django.http import JsonResponse

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .serializers import JsonSerializer

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
                'object': JsonSerializer().serialize([self.object,]),
            }
            return JsonResponse(data)
        else:
            return response