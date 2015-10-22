from django.core.urlresolvers import reverse_lazy

from django import forms
from django.forms import ModelForm, HiddenInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from .models import *

#http://blog.headspin.com/?p=581
def angular_formfield_callback(f, **kwargs):

    field = f.formfield(**kwargs)

    # guard against missing field
    if field and 'ng-model' not in field.widget.attrs:
        # set up a model for this so ng can do stuff with it
        field.widget.attrs['ng-model'] = 'dj_%s' % f.name
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
    helper.form_tag = formtag
    return helper



class RegionForm(forms.ModelForm):
    formfield_callback = angular_formfield_callback
    class Meta:
        model = Region
        exclude = ['created', 'updated', 'created_by', 'updated_by',]
    def __init__(self, *args, **kwargs):
        self.helper = setup_boostrap_helpers(formtag=True)
        self.helper.field_class = 'col-sm-4'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('rest', 'Reset', css_class='btn-warning'))
        super(RegionForm, self).__init__(*args, **kwargs)
