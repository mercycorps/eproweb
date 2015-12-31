from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ValidationError

from django import forms
from django.forms import ModelForm, inlineformset_factory, HiddenInput, Textarea

from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Button, HTML, Layout, Field, Div, Column
from crispy_forms.bootstrap import FormActions, AppendedText

from .models import Country, Office, UserProfile, Feedback


"""
A generic method used for setting up similar bootstrap properties on crispy forms
"""
def setup_boostrap_helpers(formtag=False):
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-10'
    helper.html5_required = True
    helper.form_show_labels = True
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.form_show_errors = True
    helper.form_tag = formtag
    return helper


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['reporter_role', 'issue_type', 'summary', 'description', 'reference']
        widgets = {'description': Textarea(attrs={'cols': 30, 'rows': 3}),}

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.helper = setup_boostrap_helpers(formtag=True)
        self.helper.form_id = 'id_feedback_form'
        self.helper.form_action = reverse_lazy('feedback_add')
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-9'
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-sm btn-primary'))
