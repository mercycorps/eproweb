import operator
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.generic import TemplateView, FormView, View, DeleteView, CreateView
from django.views.generic.dates import ArchiveIndexView, MonthArchiveView, YearArchiveView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.forms import inlineformset_factory
from django.utils import timezone

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from .models import Feedback, FeedbackVotesByUser, Comment, Tag, IssueStatus, Attachment
from .forms import FeedbackForm, CommentForm, AttachmentFormSet, AttachmentFormSetHelper
from .mixins import FeedbackMixin
from .utils import prepare_query_params



class FeedbackListView(FeedbackMixin, ListView):
    """
    PR List View
    """
    model = Feedback
    template_name = 'feedback/feedback_list.html'
    context_object_name = 'feedback'

    def get_queryset(self):
        search = self.request.GET.get('search', None)
        # Had to do the following
        # 1. create fulltext index summary_index on feedback_feedback(summary);
        # 2. create fulltext index description_index on feedback_feedback(description)
        args = ( Q( summary__search = search ) | Q( description__search = search ), )
        kwargs = prepare_query_params(self.request.GET)
        qs = Feedback.objects.filter(*args if search else (), **kwargs)
        return qs


class FeedbackCreateView(SuccessMessageMixin, FeedbackMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'feedback/feedback.html'
    success_message = "Thank you for providing feedback."

    def get_context_data(self, **kwargs):
        context = super(FeedbackCreateView, self).get_context_data(**kwargs)
        # if it is a GET request, then include an empty attachment formset
        if not self.request.POST:
            attachment_formset = AttachmentFormSet(instance=None)
            context['attachment_formset'] = attachment_formset
            context['attachment_formset_helper'] = AttachmentFormSetHelper()
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        form.instance.status = IssueStatus.objects.get(status="Open")
        self.object = form.save()
        tagz = self.request.POST.get('tagz').split(",")
        for tag_id in tagz:
            try:
                tag_id = int(tag_id)
                tag = Tag.objects.get(pk=tag_id)
            except ValueError:
                tag, created = Tag.objects.get_or_create(tag=tag_id, defaults={'created': self.request.user.userprofile})
            self.object.tags.add(tag)
        attachment_formset = AttachmentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if attachment_formset.is_valid():
            attachment_formset.save()
        return super(FeedbackCreateView, self).form_valid(form)


class FeedbackDetailView(FeedbackMixin, DetailView):
    model = Feedback
    template_name = "feedback/feedback_detail.html"

    def get_context_data(self, **kwargs):
        context = super(FeedbackDetailView, self).get_context_data(**kwargs)
        context['comment_tree'] = Comment.objects.filter(feedback=self.object.pk).order_by('-path')
        context['form'] = CommentForm(initial={'feedback': self.object})
        return context

class FeedbackArchiveIndexView(FeedbackMixin, ArchiveIndexView):
    """
    A list view showing the "latest" objects, by created date.
    """
    queryset = Feedback.objects.all()
    date_field = "created"
    allow_future = True
    allow_empty = True
    context_object_name = 'feedback'
    template_name = "feedback/feedback_list.html"


class FeedbackYearArchiveView(FeedbackMixin, YearArchiveView):
    """
    Annual View of Feedback entries by created date.
    """
    queryset = Feedback.objects.all()
    date_field = "created"
    make_object_list = True
    allow_future = True
    template_name = "feedback/archive_year.html"
    context_object_name = 'feedback'


class FeedbackMonthArchiveView(FeedbackMixin, MonthArchiveView):
    """
    Monthly view of Feedback entries by created month
    """
    queryset = Feedback.objects.all()
    date_field = "created"
    allow_future = True
    paginate_by=12
    #month_format='%m' # month number
    template_name = "feedback/archive_month.html"
    context_object_name = 'feedback'


class CommentCreateView(FeedbackMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "feedback/feedback_detail.html"
    context_object_name = "comment"

    def form_valid(self, form):
        form.instance.created_by = self.request.user.userprofile
        temp = form.save(commit=False)
        parent = form['parent'].value()
        if parent == '':
            #Set a blank path then save it to get an ID
            temp.path = []
            temp.save()
            temp.path = [temp.id]
        else:
            #Get the parent node
            node = Comment.objects.get(id=parent)
            temp.depth = node.depth + 1
            temp.path = eval(str(node.path))

            #Store parents path then apply comment ID
            temp.save()
            temp.path.append(temp.id)
        #Final save for parents and children
        temp.save()

        return super(CommentCreateView, self).form_valid(form)


class FeedbackVotesByUserView(View):

    def dispatch(self, *args, **kwargs):
        is_vote_change = False
        feedback_id = self.request.GET.get("feedback_id", None)
        if feedback_id is None:
            messages.error(self.request, "Nothing to vote on")
            return JsonResponse({"error": "Nothing to vote on"})

        feedback = Feedback.objects.get(pk=feedback_id)
        vote_value = self.request.GET.get("voted", None)
        if vote_value == "None" or vote_value == "false" or vote_value == 0:
            voted = False
        else:
            voted = True
        user_vote, created = FeedbackVotesByUser.objects.get_or_create(
            voter=self.request.user.userprofile, feedback=feedback, defaults={'voted': voted})

        if not created:
            # Do Not allow double voting for the same feedback_id and same user_id
            if voted and user_vote.voted or not voted and not user_vote.voted:
                messages.error(self.request, "You can change your vote but cannot double it.")
                return JsonResponse({"error": "You can change your vote but cannot double it."})

            # If the db value for voted is not the same as the voted values just received from browser then it is a vote change so allow it.
            is_vote_change = True
            user_vote.voted = voted
            user_vote.updated_by = self.request.user.userprofile
            user_vote.save()

        if is_vote_change:
            if voted:
                # reduce the count by one for undoing previous vote
                feedback.votes_dn = int(feedback.votes_dn) - 1
            else:
                # reduce the count by one for undoing previous vote
                feedback.votes_up = int(feedback.votes_up) - 1

        # now bump up the the value for this new change/addition
        if voted:
            feedback.votes_up = int(feedback.votes_up) + 1
        else:
            feedback.votes_dn = int(feedback.votes_dn) + 1

        # Finally save it.
        feedback.save()
        #messages.success(self.request, "Your vote has been saved")

        return JsonResponse({"votes_up_count": feedback.votes_up, "votes_dn_count": feedback.votes_dn})
