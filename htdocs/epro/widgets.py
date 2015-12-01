"""
Form Widget classes specific to the eProWeb
"""
from __future__ import unicode_literals
from django import forms
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.utils.html import (
    escape, escapejs, format_html, format_html_join, smart_urlquote,
)
from django.forms.utils import flatatt
from django.utils.encoding import smart_unicode, smart_text
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.translation import ugettext as _


class AngularAutoCompleteSelect(forms.Select):
    """
    A Select for Anugular ui-select .
    """

    def __init__(self, verbose_name, is_stacked, attrs=None, choices=()):
        self.verbose_name = verbose_name
        self.is_stacked = is_stacked
        super(AngularAutoCompleteSelect, self).__init__(attrs, choices)

    def render(self, name, value, attrs=None, choices=()):
        if attrs is None:
            attrs = {}
        attrs['class'] = 'selectfilter'
        if self.is_stacked:
            attrs['class'] += 'stacked'
        if value == None: value = ''
        str_value = smart_text(value)

        output = [u'<ui-select%s>' % flatatt(attrs)]

        for k, v in self.choices:
            option_value = smart_text(k)
            option_label = smart_text(v)
            selected_html = (option_value == str_value) and u' selected="selected"' or ''
            output.append(u'<option value="%s"%s>%s</option>' % (escape(option_value), selected_html, escape(option_label)))
        output.append(u'</ui-select>')
        """
        output = [
            super(FilteredSelectMultiple, self).render(name, value, attrs, choices),
            '<script type="text/javascript">addEvent(window, "load", function(e) {',
            # TODO: "id_" is hard-coded here. This should instead use the
            # correct API to determine the ID dynamically.
            'SelectFilter.init("id_%s", "%s", %s); });</script>\n' % (
                name, escapejs(self.verbose_name), int(self.is_stacked),
            ),
        ]
        """
        return mark_safe(''.join(output))