from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ValidationError

from django import forms
from django.forms import ModelForm, inlineformset_factory, HiddenInput, Textarea

from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Button, HTML, Layout, Field, Div, Column
from crispy_forms.bootstrap import FormActions, AppendedText

from .models import Country, Office, UserProfile, Feedback, Comment, Attachment


"""
A generic method used for setting up similar bootstrap properties on crispy forms
"""
def setup_boostrap_helpers(formtag=False):
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    #helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-12'
    helper.html5_required = True
    helper.form_show_labels = False
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.render_required_fields = True
    helper.form_show_errors = True
    helper.form_tag = formtag
    return helper


AttachmentFormSet = inlineformset_factory(
        Feedback, Attachment,
        extra=1,
        can_delete=False,
        fields=("attachment", "feedback"))

class AttachmentFormSetHelper(FormHelper):
    """
    This is just a helper for the AttachmentFormSet defined above to make it crispier
    """
    def __init__(self, *args, **kwargs):
        super(AttachmentFormSetHelper, self).__init__(*args, **kwargs)
        self.html5_required = True
        self.form_class = 'form-horizontal'
        self.field_class = 'col-sm-12'
        self.form_tag = False
        self.render_required_fields = True
        self.disable_csrf = True
        self.form_show_labels = False



class FeedbackForm(forms.ModelForm):
    tagz = forms.CharField(label=_('Tags'), max_length=40, required=False,)

    class Meta:
        model = Feedback
        fields = ['issue_type', 'summary', 'description', 'reference', 'tagz']
        widgets = {'description': Textarea(attrs={'cols': 30, 'rows': 3}),}

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.helper = setup_boostrap_helpers(formtag=False)
        self.fields['issue_type'].empty_label = ""
        self.helper.form_id = 'id_feedback_form'
        self.helper.form_action = reverse_lazy('feedback_add')
        #self.helper.add_input(Submit('submit', 'Submit', css_class='btn-sm btn-primary'))
        self.helper.layout = Layout(
            Div(
                Column(
                    Field('issue_type',),
                    css_class="col-sm-6",
                ), Column(
                    Field('reference',),
                    css_class="col-sm-6",
                ),
                css_class="row",
            ),
            Div(
                Column(
                    Field('summary'),
                    css_class="col-sm-12",
                ),
                css_class="row",
            ),
            Div(
                Column(
                    Field('description'),
                    css_class="col-sm-12",
                ),
                css_class="row",
            ),
            Div(
                Column(
                    Field('tagz'),
                    css_class="col-sm-12",
                ),
                css_class="row",
            ),
        )

class CommentForm(forms.ModelForm):
    #Hidden value to get a child's parent
    parent = forms.CharField(widget=forms.HiddenInput(
                            attrs={'class': 'parent'}), required=False)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['feedback'].widget = forms.HiddenInput()
        self.helper = setup_boostrap_helpers(formtag=True)
        self.helper.form_show_labels = False
        self.helper.field_class = 'col-sm-12'
        self.helper.form_id = 'id_comment_form'
        self.helper.form_action = reverse_lazy('comment_add')
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-sm btn-primary'))

    class Meta:
        model = Comment
        fields = ("feedback", "content", )
        widgets = {'content': forms.Textarea(attrs={'rows': 3, 'placeholder': "Type your comment here"})}
