# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocosign', '0003_auto_20151119_2146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, editable=False, blank=True)),
                ('updated', models.DateTimeField(null=True, editable=False, blank=True)),
                ('summary', models.CharField(help_text=b'Provide a one sentence summary of the issue', max_length=80)),
                ('description', models.CharField(help_text=b'Provide detail description of the problem/bug including steps to replicate it; if it is a feature request, describe how the feature should work and what probelm will it solve', max_length=254)),
                ('reference', models.URLField(help_text=b'Include the link to the page, where the bug/problem occurs or if applicable where the feature should be implemented', null=True, blank=True)),
                ('resolution', models.CharField(help_text=b'Explaining the action taken on this issue', max_length=254, null=True, blank=True)),
                ('annotation', models.CharField(help_text=b'Notes for the person working on resolving this issue.', max_length=250, null=True, blank=True)),
                ('votes_up', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('votes_dn', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='feedback_feedback_created', blank=True, to='djangocosign.UserProfile', null=True)),
            ],
            options={
                'verbose_name': 'User Feedback',
            },
        ),
        migrations.CreateModel(
            name='IssueStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, editable=False, blank=True)),
                ('updated', models.DateTimeField(null=True, editable=False, blank=True)),
                ('status', models.CharField(unique=True, max_length=100)),
                ('created_by', models.ForeignKey(related_name='feedback_issuestatus_created', blank=True, to='djangocosign.UserProfile', null=True)),
                ('updated_by', models.ForeignKey(related_name='feedback_issuestatus_updated', blank=True, to='djangocosign.UserProfile', null=True)),
            ],
            options={
                'verbose_name': 'Issue Status',
            },
        ),
        migrations.CreateModel(
            name='IssueType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, editable=False, blank=True)),
                ('updated', models.DateTimeField(null=True, editable=False, blank=True)),
                ('issue_type', models.CharField(unique=True, max_length=100)),
                ('created_by', models.ForeignKey(related_name='feedback_issuetype_created', blank=True, to='djangocosign.UserProfile', null=True)),
                ('updated_by', models.ForeignKey(related_name='feedback_issuetype_updated', blank=True, to='djangocosign.UserProfile', null=True)),
            ],
            options={
                'verbose_name': 'Issue Type',
            },
        ),
        migrations.CreateModel(
            name='ReporterRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, editable=False, blank=True)),
                ('updated', models.DateTimeField(null=True, editable=False, blank=True)),
                ('reporter_role', models.CharField(unique=True, max_length=100)),
                ('created_by', models.ForeignKey(related_name='feedback_reporterrole_created', blank=True, to='djangocosign.UserProfile', null=True)),
                ('updated_by', models.ForeignKey(related_name='feedback_reporterrole_updated', blank=True, to='djangocosign.UserProfile', null=True)),
            ],
            options={
                'verbose_name': 'Reporter Role',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, editable=False, blank=True)),
                ('updated', models.DateTimeField(null=True, editable=False, blank=True)),
                ('tag', models.CharField(max_length=20)),
                ('created_by', models.ForeignKey(related_name='feedback_tag_created', blank=True, to='djangocosign.UserProfile', null=True)),
                ('updated_by', models.ForeignKey(related_name='feedback_tag_updated', blank=True, to='djangocosign.UserProfile', null=True)),
            ],
            options={
                'verbose_name': 'Tag',
            },
        ),
        migrations.AddField(
            model_name='feedback',
            name='issue_type',
            field=models.ForeignKey(related_name='feedback', to='feedback.IssueType'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='reporter',
            field=models.ForeignKey(related_name='feedback', to='djangocosign.UserProfile'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='reporter_role',
            field=models.ForeignKey(related_name='feedback', to='feedback.ReporterRole'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='status',
            field=models.ForeignKey(related_name='feedback', blank=True, to='feedback.IssueStatus', null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='tags',
            field=models.ManyToManyField(related_name='feedback', to='feedback.Tag'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='updated_by',
            field=models.ForeignKey(related_name='feedback_feedback_updated', blank=True, to='djangocosign.UserProfile', null=True),
        ),
    ]
