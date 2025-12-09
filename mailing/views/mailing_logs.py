from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count, Max, Q
from django.views.generic import ListView

from mailing.models import Mailing, MailingLog


class MailingLogListView(LoginRequiredMixin, ListView):
    model = MailingLog
    template_name = "mailing/mailing_logs.html"
    context_object_name = "mailing_log"
    paginate_by = 6

    cache_timeout = 120

    def get_queryset(self):
        """
        Ограничиваем логи:
        - обычный пользователь видит только свои рассылки;
        - менеджер с правом can_view_all_mailings видит всё.
        """
        qs = super().get_queryset().select_related("mailing", "mailing__message", "mailing__owner", "client")

        user = self.request.user

        if user.has_perm("mailing.can_view_all_mailings"):
            return qs

        return qs.filter(mailing__owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = getattr(self, "object_list", None) or self.get_queryset()
        user = self.request.user
        cache_prefix = self._get_cache_prefix(user)

        counters = cache.get(f"{cache_prefix}:counters")

        if counters is None:
            total_attempts = qs.count()
            success_count = qs.filter(status="success").count()
            failed_count = qs.filter(status="failed").count()

            if total_attempts:
                success_rate = round(success_count / total_attempts * 100)
                failed_rate = 100 - success_rate
            else:
                success_rate = 0
                failed_rate = 0

            if user.has_perm("mailing.can_view_all_mailings"):
                total_mailings = Mailing.objects.count()
            else:
                total_mailings = Mailing.objects.filter(owner=user).count()

            counters = {
                "total_mailings": total_mailings,
                "total_messages": success_count,
                "successful_attempts": success_count,
                "failed_attempts": failed_count,
                "success_rate": success_rate,
                "failed_rate": failed_rate,
            }

            cache.set(f"{cache_prefix}:counters", counters, self.cache_timeout)

        mailings_stats = cache.get(f"{cache_prefix}:mailings_stats")

        if mailings_stats is None:
            mailings_stats_qs = (
                Mailing.objects.filter(mailinglog__in=qs)
                .distinct()
                .annotate(
                    total_attempts=Count("mailinglog"),
                    success_count=Count(
                        "mailinglog",
                        filter=Q(mailinglog__status="success"),
                    ),
                    failed_count=Count(
                        "mailinglog",
                        filter=Q(mailinglog__status="failed"),
                    ),
                    last_attempt_time=Max("mailinglog__attempt_time"),
                )
                .select_related("message")
            )

            mailings_stats = list(mailings_stats_qs)

            for mailing in mailings_stats:
                if mailing.total_attempts:
                    mailing.success_rate = round(mailing.success_count / mailing.total_attempts * 100)
                else:
                    mailing.success_rate = 0

            cache.set(f"{cache_prefix}:mailings_stats", mailings_stats, self.cache_timeout)

        last_attempts = cache.get(f"{cache_prefix}:last_attempts")

        if last_attempts is None:
            last_attempts = list(qs.order_by("-attempt_time")[:10])
            cache.set(f"{cache_prefix}:last_attempts", last_attempts, self.cache_timeout)

        context.update(
            {
                **counters,
                "mailings_stats": mailings_stats,
                "last_attempts": last_attempts,
            }
        )

        return context

    @staticmethod
    def _get_cache_prefix(user) -> str:
        if user.has_perm("mailing.can_view_all_mailings"):
            return "mailinglogs:all"

        return f"mailinglogs:user:{user.pk}"
