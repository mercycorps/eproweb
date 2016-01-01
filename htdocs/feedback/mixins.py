import json
import datetime
import random
from django.conf import settings
from django.db.models import Count
from .models import Feedback, IssueType, IssueStatus, Tag

class FeedbackMixin(object):
    def get_context_data(self, **kwargs):
        context = super(FeedbackMixin, self).get_context_data(**kwargs)
        context['my_issues_count'] = Feedback.objects.filter(created_by=self.request.user.userprofile).count()
        context['archive_data'] = get_feedback_archive_info(self)
        context['issue_types'] = get_issue_types(self)
        context['issues_by_status'] = get_issues_by_status(self)
        context['tags'] = get_tag_cloud(self)
        return context


def get_feedback_archive_info(self):
    """
    This is to ge a count of feedback entries by month and year.
    """
    #feedback_entries = Feedback.objects.raw("select id, year(created) as year, month(created) as month, count(id) as num_entries from feedback_feedback  group by month order by year, month")
    feedback_entries = Feedback.objects.all().\
        annotate(year=DateTime("created", "year", pytz.timezone("Etc/UTC"))).\
        annotate(month=DateTime("created", "month", pytz.timezone("Etc/UTC"))).\
        values("year", "month").\
        annotate(year_count=Count('year')).\
        annotate(month_count=Count('month')).\
        order_by("-year")
    prev_year = None
    years = {}
    months = []
    year_count = 0
    for f in feedback_entries:
        if prev_year is not None and prev_year != f.year:
            years[prev_year] = [year_count, months]
            months = []
            year_count = 0
        month_name = datetime.date(1900, f.month, 1).strftime('%b')
        months.append([month_name, f.num_entries])
        prev_year = f.year
        year_count = year_count + f.num_entries
    if prev_year:
        years[prev_year] = [year_count, months]

    return years


def get_issue_types(self):
    issue_types = IssueType.objects.filter(feedback__isnull=False).annotate(frequency=Count('feedback')).order_by('issue_type')
    return issue_types


def get_issues_by_status(self):
    issues_by_status = IssueStatus.objects.all().annotate(frequency=Count('feedback')).order_by('status')
    return issues_by_status


def get_tag_cloud(self):
    tags = Tag.objects.filter(feedback__isnull=False).annotate(frequency=Count('feedback')).order_by('frequency')

    if not tags:
        return {}

    # This is the number of occurences for the most frequent tag.
    lo_freq = tags[0].frequency

    # This is the number of occurences for the least frequent tag.
    hi_freq = tags[len(tags) -1].frequency

    # The maximum font-size of the largest (most frequent) tag
    max_fontsize = 1.7

    # The minimum font-size of the smallest (least frequent) tag
    min_fontsize = 0.8

    # The display font-size used by the current tag
    display_fontsize = 0

    tags_dict = []
    if hi_freq - lo_freq != 0:
        multiplier = (max_fontsize-min_fontsize)/(hi_freq-lo_freq)
    else:
        multiplier = 1
    multiplier = float("{0:.2f}".format(multiplier))

    colors = ["#728FCE", "#357EC7", "#008080", "#254117", "#E2A76F", "#C88141", "#6F4E37", "#E78A61", "#C24641", "#7D0541", "#583759", "#837E7C", "#2C3539"]

    tags = Tag.objects.filter(feedback__isnull=False).annotate(frequency=Count('feedback'))

    for t in tags:
        display_fontsize =  min_fontsize + (hi_freq-(hi_freq-(t.frequency-lo_freq))) * multiplier
        display_fontsize = float("{0:.2f}".format(display_fontsize))
        font_color =  random.choice(colors) #''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        tags_dict.append({'id': t.id, 'tag':t.tag, 'frequency': t.frequency, 'fontsize': display_fontsize, 'color': font_color})

    return tags_dict
