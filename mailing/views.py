from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView

from mailing.models import Mailing, Client


class MailingTemplateView(TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='started').count()
        context['unique_clients'] = Client.objects.count()
        return context


class RecipientListView(LoginRequiredMixin,ListView):
    model = Client
    template_name = "mailing/recipient_list.html"
    context_object_name = "clients"
    paginate_by = 6

    def get_queryset(self):
        return Client.objects.all()



# class MessageTemplateView(TemplateView):
#     template_name = "mailing/message_list.html"
#
#
# class MailingListTemplateView(TemplateView):
#     template_name = "mailing/mailing_list.html"



