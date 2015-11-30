import json

from django.contrib import messages

class AjaxMessaging(object):
    """
    To make django error messages set by django.contrib.messages framework
    are shown in templates when AJAx requests are made.

    Usage:
    1. add this middleware to the settings file's middleware list.
    2. In your app.js file, define a global $(document).ajaxComplete method and
    then iterate over all the messages that may be available in the json response; see below:
    $( document )
        .ajaxComplete(function(e, xhr, settings) {
            var contentType = xhr.getResponseHeader("Content-Type");

            if (contentType == "application/javascript" || contentType == "application/json") {
                var json = $.parseJSON(xhr.responseText);

                $.each(json.django_messages, function (i, item) {
                    createAlert(item.extra_tags, item.message, false);
                });
            }
        })
        .ajaxError(function(e, xhr, settings, thrownError) {
            createAlert("danger", "Error " + xhr.status + ": " +  thrownError, false);
        });
    """
    def process_response(self, request, response):
        if request.is_ajax():
            if response['Content-Type'] in ["application/javascript", "application/json"]:
                try:
                    content = json.loads(response.content)
                except ValueError as e:
                    return response

                django_messages = []

                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                if django_messages:
                    content['django_messages'] = django_messages
                    response.content = json.dumps(content)
        return response