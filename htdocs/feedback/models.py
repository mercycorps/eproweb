from datetime import date, datetime, timedelta
from django.core.urlresolvers import reverse_lazy
from django.db import models

from django.utils import timezone
#from django.utils.timezone import utc
from django.utils import timezone

from djangocosign.models import Country, Office, UserProfile

from .utils import smart_list



class CommonBaseAbstractModel(models.Model):
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name="%(app_label)s_%(class)s_created")
    updated_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name="%(app_label)s_%(class)s_updated")
    created = models.DateTimeField(editable=False, blank=True, null=True)
    updated = models.DateTimeField(editable=False, blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        #now_utc = datetime.datetime.utcnow().replace(tzinfo=utc)
        now_utc = timezone.now()
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


class IssueStatus(CommonBaseAbstractModel):
    status = models.CharField(unique=True, max_length=100, null=False, blank=False)

    def __unicode__(self):
        return u'%s' % self.status

    def __str__(self):
        return '%s' % self.status

    class Meta(object):
        verbose_name = 'Issue Status'


class Tag(CommonBaseAbstractModel):
    tag = models.CharField(max_length=30, null=False, blank=False)

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
    issue_type = models.ForeignKey(IssueType, related_name="feedback", null=False, blank=False, on_delete=models.CASCADE,
        help_text="<span style='color:red'>*</span> The type of issue your are reporting.")
    summary = models.CharField(max_length=120, null=False, blank=False, db_index=True,
        help_text="<span style='color:red'>*</span> Provide a one sentence summary of the issue")
    description = models.CharField(max_length=254, null=False, blank=False,
        help_text="<span style='color:red'>*</span> Provide detail description of the problem/bug including steps to replicate it; if it is a feature request, describe how the feature should work and what probelm will it solve")
    reference = models.URLField(null=True, blank=True,
        help_text="Link to the page, where the issue occurs.")
    tags = models.ManyToManyField(Tag, related_name='feedback', help_text="Apply tags so that it is easier to find it later")
    status = models.ForeignKey(IssueStatus, related_name="feedback", null=True, blank=True, on_delete=models.CASCADE)
    resolution = models.CharField(max_length=254, null=True, blank=True, help_text="Explaining the action taken on this issue")
    annotation = models.CharField(max_length=250, null=True, blank=True, help_text="Notes for the person working on resolving this issue.")
    votes_up = models.PositiveIntegerField(default=0, blank=True, null=True)
    votes_dn = models.PositiveIntegerField(default=0, blank=True, null=True)
    #TODO: Allow attachments to be uploaded to Google Drive

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
        #return reverse_lazy('feedback_list') #args=[str(self.id)])


class Comment(CommonBaseAbstractModel):
    feedback = models.ForeignKey(Feedback, related_name="comments", null=False, blank=False, on_delete=models.CASCADE)
    content = models.CharField(max_length=254, null=False, blank=False)
    path = models.CommaSeparatedIntegerField(max_length=250, null=False, blank=False, editable=False)
    depth = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return u'%s' % self.content

    def __str__(self):
        return '%s' % self.content

    class Meta:
        verbose_name = 'Comment'

    def clean_csv_fields(self):
        """Convert all the CommaSeparatedIntegerField values to lists."""
        # this function is applied to each element in the list
        # in this case just cast it to an integer, ensuring that
        # we get a list of ints back out
        func = lambda x: int(x)
        self.path = smart_list(self.path, func=func)

    def get_absolute_url(self):
        """
        Used when we need to link to a specific feedback entry.
        """
        return reverse_lazy('feedback_view', kwargs={'pk': self.feedback.pk})


class FeedbackVotesByUser(CommonBaseAbstractModel):
    """
    This model keeps track of users votes per issue/feedback to make sure someone does not vote more than once
    """
    voter = models.ForeignKey(UserProfile, blank=True, null=True, related_name="votes")
    feedback = models.ForeignKey(Feedback, blank=True, null=True, related_name="votes")
    voted = models.BooleanField(null=False, blank=False)

    class Meta:
        unique_together = (("voter", "feedback"),)


class Attachment(CommonBaseAbstractModel):
    feedback = models.ForeignKey(Feedback, related_name='attachments', on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='uploads/issues/%Y/%m/%d/', help_text="You may attach a file or screenshot if it helps to explain this issue better.")

    def get_absolute_url(self):
        """
        Used when we need to link to a specific blog post.
        """
        return reverse_lazy('feedback_view', args=[str(self.feedback.pk)])


class Notification(CommonBaseAbstractModel):
    user = models.ForeignKey(UserProfile, related_name='notifications', null=False, blank=False, on_delete=models.CASCADE)
    message = models.CharField(max_length=250, null=False, blank=False)
    color = models.CharField(max_length=7, null=False, blank=False, default="#cccccc")
    icon = models.CharField(max_length=20, null=False, blank=False, default="info")
    seen = models.BooleanField(default=False, null=False, blank=False)
    seen_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(default=date.today()+timedelta(days=30))

    def save(self, *args, **kwargs):
        notifications = Notification.objects.filter(expiration_date__lte=date.today())
        if notifications.count() > 30:
            for n in notifications:
                n.delete()


    def add(klass, users, message):
        for user in users:
            notification = klass(user=user, message=message)
            notification.save()

