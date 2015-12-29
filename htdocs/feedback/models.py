import datetime, time

from django.core.urlresolvers import reverse_lazy
from django.db import models

from django.utils import timezone
from django.utils.timezone import utc

from djangocosign.models import Country, Office, UserProfile

class CommonBaseAbstractModel(models.Model):
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name="%(app_label)s_%(class)s_created")
    updated_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name="%(app_label)s_%(class)s_updated")
    created = models.DateTimeField(editable=False, blank=True, null=True)
    updated = models.DateTimeField(editable=False, blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        now_utc = datetime.datetime.utcnow().replace(tzinfo=utc)
        if self.id:
            self.updated = now_utc
        else:
            self.created = now_utc
        super(CommonBaseAbstractModel, self).save(*args, **kwargs)


class IssueType(CommonBaseAbstractModel):
    issue_type = models.CharField(unique=True, max_length=100, null=False, blank=False)

    def __unicode__(self):
        return u'%s' % self.issue_type

    def __str__(self):
        return '%s' % self.issue_type

    class Meta(object):
        verbose_name = 'Issue Type'


class ReporterRole(CommonBaseAbstractModel):
    reporter_role = models.CharField(unique=True, max_length=100, null=False, blank=False)

    def __unicode__(self):
        return u'%s' % self.reporter_role

    def __str__(self):
        return '%s' % self.reporter_role

    class Meta(object):
        verbose_name = 'Reporter Role'


class IssueStatus(CommonBaseAbstractModel):
    status = models.CharField(unique=True, max_length=100, null=False, blank=False)

    def __unicode__(self):
        return u'%s' % self.status

    def __str__(self):
        return '%s' % self.status

    class Meta(object):
        verbose_name = 'Issue Status'


class Tag(CommonBaseAbstractModel):
    tag = models.CharField(max_length=20, null=False, blank=False)

    def __unicode__(self):
        return u'%s' % self.tag

    def __str__(self):
        return '%s' % self.tag
    class Meta:
        verbose_name = 'Tag'

    def get_absolute_url(self):
        """
        Used when we need to link to a specific Tag.
        """
        return reverse('tag', args=[str(self.id)])


class Feedback(CommonBaseAbstractModel):
    reporter = models.ForeignKey(UserProfile, related_name="feedback", null=False, blank=False, on_delete=models.CASCADE)
    reporter_role = models.ForeignKey(ReporterRole, related_name="feedback", null=False, blank=False, on_delete=models.CASCADE)
    issue_type = models.ForeignKey(IssueType, related_name="feedback", null=False, blank=False, on_delete=models.CASCADE)
    summary = models.CharField(max_length=80, null=False, blank=False, help_text="Provide a one sentence summary of the issue")
    description = models.CharField(max_length=254, null=False, blank=False,
        help_text="Provide detail description of the problem/bug including steps to replicate it; if it is a feature request, describe how the feature should work and what probelm will it solve")
    reference = models.URLField(null=True, blank=True,
        help_text="Include the link to the page, where the bug/problem occurs or if applicable where the feature should be implemented")
    tags = models.ManyToManyField(Tag, related_name='feedback')
    status = models.ForeignKey(IssueStatus, related_name="feedback", null=True, blank=True, on_delete=models.CASCADE)
    resolution = models.CharField(max_length=254, null=True, blank=True, help_text="Explaining the action taken on this issue")
    annotation = models.CharField(max_length=250, null=True, blank=True, help_text="Notes for the person working on resolving this issue.")
    votes_up = models.PositiveIntegerField(default=0, blank=True, null=True)
    votes_dn = models.PositiveIntegerField(default=0, blank=True, null=True)

    def get_absolute_url(self):
        return reverse_lazy('feedback', kwargs={'pk': self.pk})

    def __unicode__(self):
        return u'%s' % self.summary

    def __str__(self):
        return '%s' % self.summary

    class Meta:
        verbose_name = 'User Feedback'

    def get_absolute_url(self):
        """
        Used when we need to link to a specific feedback entry.
        """
        return reverse_lazy('feedback_view', kwargs={'pk': self.pk}) #args=[str(self.id)])
