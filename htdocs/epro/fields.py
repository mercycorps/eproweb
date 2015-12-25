from decimal import Decimal

from django.core.validators import MinValueValidator

from django.db import models
from django.db.models import IntegerField, DecimalField

from django import forms
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


class LazyChoiceField(forms.ChoiceField):
    '''
    A Lazy ChoiceField.
    This ChoiceField does not unwind choices until a deepcopy is called on it.
    This allows for dynamic choices generation every time an instance of a Form is created.

    Usage:
    DynamicApplicationList = []

    class MyForm(forms.Form):
        dynamic_choice = LazyChoiceField(choices = DynamicApplicationList)

    DynamicApplicationList can now be updated dynamically.
    '''
    def __init__(self, *args, **kwargs):
        # remove choices from kwargs.
        # choices should be an iterable
        self._lazy_choices = kwargs.pop('choices',())
        super(LazyChoiceField,self).__init__(*args, **kwargs)

    def __deepcopy__(self, memo):
        result = super(LazyChoiceField,self).__deepcopy__(memo)
        lz = self._lazy_choices
        if callable(lz):
            lz = lz()
        result.choices = lz
        return result


class LazyChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(LazyChoiceField, self).__init__(*args, **kwargs)

    def valid_value(self, value):
        pass
        # your custom validation code for  "value" argument goes here
        # return True if value is valid else return False
        return True

class MyForm(forms.Form):
    list_of_choices = (
        (1, 'Choice 1'),
        (2, 'Choice 2'),
        (3, 'Choice 3'),
        # ...
        (1001, 'Choice n'),
    )
    my_choice_field = LazyChoiceField(choices=list_of_choices)