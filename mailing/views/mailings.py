from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from mailing.forms import MailingForm
from mailing.models import Mailing, MailingLog
from mailing.services import run_mailing
from mailing.mixins import OwnerQuerysetMixin, OwnerAccessMixin


class MailingListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = 6

    cache_timeout = 60

    def get_queryset(self):
        """
        Возвращаем рассылки текущего пользователя (или все для менеджера)
        и обновляем статус КАЖДОГО объекта только в памяти (save=False),
        чтобы не делать лишние UPDATE-запросы к БД при открытии списка.

        Фактическое сохранение статуса в БД происходит:
        - в детальном представлении (MailingDetailView),
        - при запуске рассылки (run_mailing).
        """
        qs = (
            super()
            .get_queryset()
            .select_related("message")
            .prefetch_related("clients")
            .annotate(clients_count=Count("clients", distinct=True))
        )

        for mailing in qs:
            mailing.update_status(save=False)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.object_list
        now = timezone.now()
        user = self.request.user

        cache_key = self._get_cache_key(user)

        stats = cache.get(cache_key)

        if stats is None:
            stats = {
                "total_mailings": qs.count(),
                "created_mailings": qs.filter(status="created").count(),
                "started_mailings": qs.filter(status="started").count(),
                "finished_mailings": qs.filter(status="finished").count(),
                "active_mailings": qs.filter(
                    status="started",
                    start_time__lte=now,
                    end_time__gte=now,
                ).count(),
            }
            cache.set(cache_key, stats, self.cache_timeout)

        context.update(stats)

        context["now"] = now
        return context

    @staticmethod
    def _get_cache_key(user) -> str:
        return f"mailings:summary:user:{user.pk}"


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("mailing:mailing_list")


class MailingUpdateView(LoginRequiredMixin, OwnerAccessMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"

    def get_success_url(self):
        return reverse_lazy("mailing:mailing_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingDeleteView(LoginRequiredMixin, OwnerAccessMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingRunView(LoginRequiredMixin, View):

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        if mailing.owner != request.user and not request.user.is_superuser:
            messages.error(request, "У вас нет прав на запуск этой рассылки.")
            return redirect("mailing:mailing_detail", pk=pk)

        result = run_mailing(mailing)

        if not result["ok"]:
            messages.error(request, result["error"])
        else:
            messages.success(
                request,
                (
                    f"Рассылка запущена. Всего клиентов: {result['total']}, "
                    f"успешно: {result['success']}, с ошибками: {result['failed']}."
                ),
            )

        return redirect("mailing:mailing_list")


class MailingDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object()
        obj.update_status()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object
        now = timezone.now()

        interval_invalid = mailing.start_time >= mailing.end_time
        before_window = mailing.start_time > now
        after_window = mailing.end_time < now

        can_run = (
            not interval_invalid
            and not before_window
            and not after_window
            and mailing.status != "finished"
        )

        logs_qs = (
            MailingLog.objects
            .filter(mailing=mailing)
            .select_related("client")
            .order_by("-attempt_time")
        )

        stats = logs_qs.aggregate(
            total=Count("id"),
            success=Count("id", filter=Q(status="success")),
            failed=Count("id", filter=Q(status="failed")),
        )

        context["logs"] = logs_qs
        context["stats"] = stats
        context["interval_invalid"] = interval_invalid
        context["before_window"] = before_window
        context["after_window"] = after_window
        context["can_run"] = can_run
        context["now"] = now

        return context
