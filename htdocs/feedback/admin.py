from django.contrib import admin
from .models import *

admin.site.register(IssueType)
admin.site.register(ReporterRole)
admin.site.register(IssueStatus)
admin.site.register(Tag)
admin.site.register(Feedback)
admin.site.register(FeedbackVotesByUser)