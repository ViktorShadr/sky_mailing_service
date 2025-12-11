from django.core.cache import cache
from django.utils import timezone
from django.views.generic import TemplateView

from mailing.models import Client, Mailing


class MailingTemplateView(TemplateView):
    template_name = "mailing/index.html"

    cache_timeout = 120

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        cache_key = self._get_cache_key(user)

        stats = cache.get(cache_key)

        if stats is None:
            now = timezone.now()

            if not user.is_authenticated or getattr(user, "is_manager", False):
                mailings_qs = Mailing.objects.filter(owner__is_manager=False)
                clients_qs = Client.objects.filter(owner__is_manager=False)
            else:
                mailings_qs = Mailing.objects.filter(owner=user)
                clients_qs = Client.objects.filter(owner=user)

            stats = {
                "total_mailings": mailings_qs.count(),
                "active_mailings": mailings_qs.filter(
                    status="started",
                    start_time__lte=now,
                    end_time__gte=now,
                ).count(),
                "unique_clients": clients_qs.count(),
            }

            cache.set(cache_key, stats, self.cache_timeout)

        context.update(stats)

        return context

    @staticmethod
    def _get_cache_key(user) -> str:
        if not user.is_authenticated:
            return "dash:main:public"

        if getattr(user, "is_manager", False):
            return "dash:main:manager"

        return f"dash:main:user:{user.pk}"
