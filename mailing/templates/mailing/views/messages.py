from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from mailing.models import Message


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"
    paginate_by = 6

    def get_queryset(self):
        return Message.objects.all()