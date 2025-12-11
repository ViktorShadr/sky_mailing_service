from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from mailing.forms import MessageForm
from mailing.mixins import OwnerAccessMixin, OwnerQuerysetMixin
from mailing.models import Message


class MessageListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"
    paginate_by = 6


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("mailing:message_list")


class MessageUpdateView(LoginRequiredMixin, OwnerAccessMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"

    def get_success_url(self):
        return reverse_lazy("mailing:message_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MessageDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


class MessageDeleteView(LoginRequiredMixin, OwnerAccessMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")
