from django.dispatch import receiver
from django.db.models.signals import pre_save, post_init

from .models import Comment


# listen for the signals, and ensure that fields are cleaned
@receiver([pre_save, post_init], sender=Comment)
def _on_model_signal(sender, instance, **kwargs):
    instance.clean_csv_fields()