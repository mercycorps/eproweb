from django.core.urlresolvers import reverse_lazy
from django.core.validators import MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.db.models import PositiveIntegerField

from django import forms
from django.forms import ModelForm, HiddenInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Button, HTML
from crispy_forms.bootstrap import FormActions

from .models import *
from django.contrib.auth.models import User

from .fields import AutoCompleteSelect
from .widgets import AngularAutoCompleteSelect
from crispy_forms.layout import Layout, Field

#http://blog.headspin.com/?p=581
def angular_formfield_callback(f, **kwargs):
    #print("angular_formfield_callback called!!!")
    if isinstance(f, PositiveIntegerField):
        field = f.formfield(widget = PositiveIntWidget(), **kwargs)
    else:
        field = f.formfield(**kwargs)

    # guard against missing field
    # https://docs.djangoproject.com/en/1.8/ref/validators/
    if field:
        for v in f.validators: # Copy any model validation into the widget
            if isinstance(v, MaxValueValidator):
                field.widget.attrs['max'] = v.limit_value
            elif isinstance(v, MinValueValidator):
                field.widget.attrs['min'] = v.limit_value
            elif isinstance(v, EmailValidator):
                field.widget.attrs['type'] = 'Email'
        if 'data-ng-model' not in field.widget.attrs:
            # set up a model for this so ng can do stuff with it
            field.widget.attrs['data-ng-model'] = 'dj_%s' % f.name
            # set the model name as an attribute of the
            # init directive in case we want to know it later
            field.widget.attrs['dj_init'] =  field.__class__.__name__.lower()

    return field


"""
A generic method used for setting up similar bootstrap properties on crispy forms
"""
def setup_boostrap_helpers(formtag=False):
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-10'
    helper.label_size = ' col-sm-offset-2'
    helper.html5_required = True
    helper.form_show_labels = True
    helper.form_tag = formtag
    return helper



class PurchaseRequestForm(forms.ModelForm):
    formfield_callback = angular_formfield_callback
    class Meta:
        model = PurchaseRequest
        #exclude = ['country', 'originator', 'submission_date', 'pr_type', 'status', 'approver1', 'approval1_date', 'approver2', 'approval2_date', 'finance_reviewer', 'finance_review_date', 'currency', 'notes', 'created', 'updated', 'created_by', 'updated_by',]
        fields = ['project_reference', 'delivery_address', 'currency', 'dollar_exchange_rate', 'required_date', 'approver1', 'approver2', ]
        #widgets = {
        #    'approver1': AngularAutoCompleteSelect(verbose_name='Approver Level 1', is_stacked=True, attrs={'placeholder': u'--Approver 1--', 'ng-model': 'dj_approver1', 'class': ''})
        #}

    def __init__(self, *args, **kwargs):
        self.helper = setup_boostrap_helpers(formtag=True)
        self.helper.field_class = 'col-sm-4'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('rest', 'Reset', css_class='btn-warning'))
        self.helper.add_input(Button('cancel', 'Back', css_class='btn-default', onclick="window.history.back()"))
        self.helper.add_input(Button('cancel', "ePro", css_class='btn btn-default',onclick="javascript:location.href = '/epro/';"))
        self.helper.attrs = {'id': 'id_region_form', 'data_id': '/whatever', 'data-ng-submit': 'submit()', 'novalidate': True}
        self.helper.layout = Layout(
            Field('approver1', chosen=''),
        )
        super(PurchaseRequestForm, self).__init__(*args, **kwargs)