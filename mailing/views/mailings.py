from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from mailing.forms import MailingForm
from mailing.models import Mailing, MailingLog
from mailing.services import run_mailing


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = 6

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_mailings"] = Mailing.objects.filter(owner=self.request.user).count()
        context["started_mailings"] = Mailing.objects.filter(owner=self.request.user, status="started").count()
        context["finished_mailings"] = Mailing.objects.filter(owner=self.request.user, status="finished").count()
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


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        user = request.user

        if mailing.owner == user:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user

        is_owner = self.object.owner == user

        if is_owner:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied


class MailingRunView(LoginRequiredMixin, View):

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        if mailing.owner != request.user and not request.user.is_staff:
            messages.error(request, "У вас нет прав на запуск этой рассылки.")
            return redirect("mailing_detail", pk=pk)

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


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return qs
        return qs.filter(owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object

        logs = MailingLog.objects.filter(mailing=mailing).order_by("-attempt_time")
        context["logs"] = logs
        return context
