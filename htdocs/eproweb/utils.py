from decimal import Decimal
import json
from math import floor
import re
from time import time

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import DecimalField


def is_int(value):
    try:
        int(value)
    except ValueError:
        return False
    else:
        return True


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
