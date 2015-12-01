from decimal import Decimal

from django.core.validators import MinValueValidator

from django.db import models
from django.db.models import IntegerField, DecimalField

from django.forms.utils import ValidationError
from django.utils.translation import ugettext_lazy as _

from .widgets import AngularAutoCompleteSelect



class AutoCompleteSelect(models.ForeignKey):
    def formfield(self, **kwargs):
        kwargs['widget'] = AngularAutoCompleteSelect
        return super(AutoCompleteSelect, self).formfield(**kwargs)


class USDCurrencyField(DecimalField):
    """
    DecimalField with useful defaults for USD currency.
    """
    def __init__(self, max_digits=10, decimal_places=2, default=Decimal('0.00'), **kwargs):
        validators = kwargs.pop('validators', [MinValueValidator(0.0)])
        super(USDCurrencyField, self).__init__(
            max_digits=max_digits,
            decimal_places=decimal_places,
            validators=validators,
            default=default,
            **kwargs
        )
