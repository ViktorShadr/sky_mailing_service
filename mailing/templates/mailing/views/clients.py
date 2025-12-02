from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from mailing.models import Client


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/recipient_list.html"
    context_object_name = "clients"
    paginate_by = 6

    def get_queryset(self):
        return Client.objects.all()