from django.utils import timezone
from django.views.generic import TemplateView

from mailing.models import Client, Mailing


class MailingTemplateView(TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context["total_mailings"] = Mailing.objects.count()
        context["active_mailings"] = Mailing.objects.filter(
            status="started",
            start_time__lte=now,
            end_time__gte=now,
        ).count()
        context["unique_clients"] = Client.objects.count()
        return context
