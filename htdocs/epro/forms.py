from django.core.urlresolvers import reverse_lazy, reverse

from django import forms
from django.forms import ModelForm, inlineformset_factory, HiddenInput

from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from django.views.generic.edit import CreateView, UpdateView

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Button, HTML, Layout, Field, Div, Column
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


class PurchaseRequestItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['purchase_request', 'quantity_requested', 'unit', 'description_pr', 'price_estimated_local', ]
        widgets = {'purchase_request': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(PurchaseRequestItemForm, self).__init__(*args, **kwargs)
        form_action = kwargs['initial'].pop('form_action')
        self.helper = setup_boostrap_helpers(formtag=True)
        self.helper.form_action = reverse_lazy(form_action if form_action else 'item_new')
        self.helper.form_id = 'pr_item_form'
        self.helper.add_input(Submit('submit', 'Add Item', css_class='btn-sm btn-primary'))
        self.helper.add_input(Reset('reset', 'Reset', css_class='btn-sm btn-warning'))
        self.fields['description_pr'].widget.attrs['rows'] = 3


class FinanceCodesForm(forms.ModelForm):
    class Meta:
        model = FinanceCodes
        fields = ['gl_account', 'fund_code', 'dept_code', 'office_code', 'lin_code', 'activity_code', 'employee_id',]

    def __init__(self, *args, **kwargs):
        super(FinanceCodesForm, self).__init__(*args, **kwargs)
        self.helper = setup_boostrap_helpers(formtag=True)
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-9'
        self.helper.add_input(Submit('submit', 'Add Finance Codes', css_class='btn-sm btn-primary'))
        self.helper.add_input(Reset('reset', 'Reset', css_class='btn-sm btn-warning'))
        """
        self.helper.layout = Layout(
            Div(
                Column(
                    Field('gl_account', css_class='input-sm'),
                    Field('fund_code', css_class='input-sm'),
                    Field('dept_code', css_class='input-sm'),
                    Field('office_code', css_class='input-sm'),
                    Field('lin_code', css_class='input-sm'),
                    Field('activity_code', css_class='input-sm'),
                    Field('employee_id', css_class='input-sm'),
                    css_class='col-sm-12',
                ),
                css_class='row',
            ),
            Div(
                Column(
                    FormActions(
                        Submit('submit', 'Add Finance Code', css_class='btn btn-primary btn-sm'),
                    ),
                    css_class='col-sm-12',
                ),
                css_class='row',
            ),
        )
        """


