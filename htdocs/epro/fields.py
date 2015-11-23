from .widgets import AngularAutoCompleteSelect
from django.db import models

class AutoCompleteSelect(models.ForeignKey):
    def formfield(self, **kwargs):
        kwargs['widget'] = AngularAutoCompleteSelect
        return super(AutoCompleteSelect, self).formfield(**kwargs)