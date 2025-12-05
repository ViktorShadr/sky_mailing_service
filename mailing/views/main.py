from django.utils import timezone
from django.views.generic import TemplateView

from mailing.models import Client, Mailing


class MailingTemplateView(TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        user = self.request.user

        if not user.is_authenticated:

            mailings_qs = Mailing.objects.filter(owner__is_manager=False)
            clients_qs = Client.objects.filter(owner__is_manager=False)

        elif getattr(user, "is_manager", False):

            mailings_qs = Mailing.objects.filter(owner__is_manager=False)
            clients_qs = Client.objects.filter(owner__is_manager=False)

        else:

            mailings_qs = Mailing.objects.filter(owner=user)
            clients_qs = Client.objects.filter(owner=user)

        context["total_mailings"] = mailings_qs.count()
        context["active_mailings"] = mailings_qs.filter(
            status="started",
            start_time__lte=now,
            end_time__gte=now,
        ).count()
        context["unique_clients"] = clients_qs.count()

        return context
