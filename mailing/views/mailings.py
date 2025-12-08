from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        context["total_mailings"] = qs.count()
        context["started_mailings"] = qs.filter(status="started").count()
        context["finished_mailings"] = qs.filter(status="finished").count()
        return context


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
    success_url = reverse_lazy("mailing:mailing_list")

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
        obj.update_status(queryset)
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

        context["logs"] = MailingLog.objects.filter(mailing=mailing).order_by("-attempt_time")
        context["interval_invalid"] = interval_invalid
        context["before_window"] = before_window
        context["after_window"] = after_window
        context["can_run"] = can_run
        context["now"] = now  # если захочешь где-то показать

        return context
