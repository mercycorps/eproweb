from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    name = "feedback"

    def ready(self):
        from . import signals