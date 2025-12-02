from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView, ListView

from mailing.models import Mailing, Client, Message


class MailingTemplateView(TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(
            status='started',
            start_time__lte=now,
            end_time__gte=now,
        ).count()
        context['unique_clients'] = Client.objects.count()
        return context

#  ----------------------контроллеры CRUD для Получателей рассылки---------------------------------------------------
class RecipientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/recipient_list.html"
    context_object_name = "clients"
    paginate_by = 6

    def get_queryset(self):
        return Client.objects.all()


#  ----------------------контроллеры CRUD для Сообщений---------------------------------------------------------------
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"
    paginate_by = 6

    def get_queryset(self):
        return Message.objects.all()


#  ----------------------контроллеры CRUD для Рассылок----------------------------------------------------------------
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = 6

    def get_queryset(self):
        return Mailing.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_mailings"] = Mailing.objects.count()
        context["started_mailings"] = Mailing.objects.filter(status="started").count()
        context["finished_mailings"] = Mailing.objects.filter(status="finished").count()
        return context
