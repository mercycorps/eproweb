from django.core.urlresolvers import reverse_lazy
from django.core.validators import MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.db.models import PositiveIntegerField

from django import forms
from django.forms import ModelForm, inlineformset_factory, HiddenInput

from django.contrib.auth.models import User

from django.views.generic.edit import CreateView, UpdateView

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Button, HTML, Layout, Field
from crispy_forms.bootstrap import FormActions

from .models import PurchaseRequest, Item, FinanceCodes

ItemFormset = inlineformset_factory(PurchaseRequest, Item, extra=1, fields=(
                                                                    'quantity_requested',
                                                                    'unit',
                                                                    'description_pr',
                                                                    'price_estimated_local',
                                                                    'price_estimated_usd',
                                                                    'price_estimated_local_subtotal',)
                                                                    )

class ItemFormsetHelper(FormHelper):
    """
    This is just a helper for the AttachmentFormset defined above to make it crispier
    """
    def __init__(self, *args, **kwargs):
        super(ItemFormsetHelper, self).__init__(*args, **kwargs)
        self.html5_required = True
        self.render_required_fields = True
        self.form_class = 'form-horizontal'
        self.label_class = 'col-sm-2'
        self.field_class = 'col-sm-10'
        self.form_tag = False
        self.render_required_fields = True
        self.disable_csrf = True
        self.form_show_labels = True

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

    class Meta:
        model = PurchaseRequest
        #exclude = ['country', 'originator', 'submission_date', 'pr_type', 'status', 'approver1', 'approval1_date', 'approver2', 'approval2_date', 'finance_reviewer', 'finance_review_date', 'currency', 'notes', 'created', 'updated', 'created_by', 'updated_by',]
        fields = ['project_reference', 'delivery_address', 'currency', 'dollar_exchange_rate', 'required_date', 'approver1', 'approver2', ]

    def __init__(self, *args, **kwargs):
        self.helper = setup_boostrap_helpers(formtag=False)
        # self.helper.field_class = 'col-sm-4'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('rest', 'Reset', css_class='btn-warning'))
        #self.helper.add_input(Button('cancel', 'Back', css_class='btn-default', onclick="window.history.back()"))
        #self.helper.add_input(Button('cancel', "ePro", css_class='btn btn-default',onclick="javascript:location.href = '/epro/';"))
        self.helper.attrs = {'id': 'id_pr_form'}
        super(PurchaseRequestForm, self).__init__(*args, **kwargs)