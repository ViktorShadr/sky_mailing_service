from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Max
from django.views.generic import ListView

from mailing.models import MailingLog, Mailing


class MailingLogListView(LoginRequiredMixin, ListView):
    model = MailingLog
    template_name = "mailing/mailing_logs.html"
    context_object_name = "mailing_log"
    paginate_by = 6

    def get_queryset(self):
        """
        Ограничиваем логи:
        - обычный пользователь видит только свои рассылки;
        - менеджер с правом can_view_all_mailings видит всё.
        """
        qs = (
            super()
            .get_queryset()
            .select_related("mailing", "mailing__message", "mailing__owner", "client")
        )

        user = self.request.user

        if user.has_perm("mailing.can_view_all_mailings"):
            return qs

        return qs.filter(mailing__owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        user = self.request.user

        # ===== Глобальные счётчики =====
        total_attempts = qs.count()
        success_count = qs.filter(status="success").count()
        failed_count = qs.filter(status="failed").count()

        if total_attempts:
            success_rate = round(success_count / total_attempts * 100)
            failed_rate = 100 - success_rate
        else:
            success_rate = 0
            failed_rate = 0

        # Сколько рассылок всего у пользователя (или вообще, если менеджер)
        if user.has_perm("mailing.can_view_all_mailings"):
            total_mailings = Mailing.objects.count()
        else:
            total_mailings = Mailing.objects.filter(owner=user).count()

        # Сколько сообщений реально было отправлено — считаем только успешные попытки
        total_messages = success_count

        # ===== Статистика по каждой рассылке =====
        # Берём только те рассылки, по которым есть логи в qs
        mailings_stats = (
            Mailing.objects
            .filter(mailinglog__in=qs)
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

        # Добавим каждому объекту процент успешности
        for mailing in mailings_stats:
            if mailing.total_attempts:
                mailing.success_rate = round(
                    mailing.success_count / mailing.total_attempts * 100
                )
            else:
                mailing.success_rate = 0

        # ===== Последние попытки отправки =====
        last_attempts = qs.order_by("-attempt_time")[:10]

        # Кладём всё в контекст — имена полей совпадают с теми,
        # что я использовал в шаблоне статистики
        context.update(
            {
                "total_mailings": total_mailings,
                "total_messages": total_messages,
                "successful_attempts": success_count,
                "failed_attempts": failed_count,
                "success_rate": success_rate,
                "failed_rate": failed_rate,
                "mailings_stats": mailings_stats,
                "last_attempts": last_attempts,
            }
        )

        return context
