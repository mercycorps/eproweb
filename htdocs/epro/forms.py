from django.core.urlresolvers import reverse_lazy
from django.core.validators import MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.db.models import PositiveIntegerField

from django import forms
from django.forms import ModelForm, inlineformset_factory, HiddenInput

from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from django.views.generic.edit import CreateView, UpdateView

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Button, HTML, Layout, Field
from crispy_forms.bootstrap import FormActions

from .models import PurchaseRequest, Item, FinanceCodes


"""
A generic method used for setting up similar bootstrap properties on crispy forms
"""
def setup_boostrap_helpers(formtag=False):
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-10'
    #helper.label_size = ' col-sm-offset-2'
    helper.html5_required = True
    helper.form_show_labels = True
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.form_show_errors = True
    helper.form_tag = formtag

    return helper


class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['country', 'office', 'project_reference', 'delivery_address', 'currency', 'dollar_exchange_rate', 'required_date', 'approver1', 'approver2', 'originator']
        widgets = {'originator': forms.HiddenInput()}
        labels = {
            'country': _('Originating Country'),
            'office': _('Originating Office'),
            'dollar_exchange_rate': _('USD Exchange rate'),
        }

    def __init__(self, *args, **kwargs):
        super(PurchaseRequestForm, self).__init__(*args, **kwargs)
        self.helper = setup_boostrap_helpers(formtag=True)
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-sm btn-primary'))
        self.helper.add_input(Reset('reset', 'Reset', css_class='btn-sm btn-warning'))
        self.helper.attrs = {'id': 'id_prform', }
