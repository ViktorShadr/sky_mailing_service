from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from mailing.models import Client, Mailing, MailingLog
from users.mixins import ManagerRequiredMixin
from users.models import User


class ManagerDashboardView(ManagerRequiredMixin, TemplateView):
    """Главная панель управления менеджера с общей статистикой."""

    template_name = "users/manager/manager_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        users_qs = User.objects.filter(is_manager=False).exclude(is_staff=True, is_superuser=True)

        context["total_users"] = users_qs.count()
        context["blocked_users"] = users_qs.filter(is_active=False).count()
        context["active_users"] = users_qs.filter(is_active=True).count()

        mailings_qs = Mailing.objects.filter(owner__is_manager=False)
        context["total_mailings"] = mailings_qs.count()

        context["active_mailings"] = mailings_qs.filter(status="started").count()
        context["disabled_mailings"] = mailings_qs.exclude(status="started").count()

        return context


class ManagerClientsListView(PermissionRequiredMixin, ManagerRequiredMixin, ListView):
    """Список всех клиентов в системе для просмотра менеджером."""

    model = Client
    template_name = "users/manager/manager_clients_list.html"
    context_object_name = "clients"
    paginate_by = 10
    permission_required = "mailing.can_view_all_clients"

    def get_queryset(self):
        return Client.objects.select_related("owner").all()


class ManagerClientDetailView(PermissionRequiredMixin, ManagerRequiredMixin, DetailView):
    """Детальная информация о клиенте для менеджера."""

    model = Client
    template_name = "users/manager/manager_client_detail.html"
    context_object_name = "client"
    permission_required = "mailing.can_view_all_clients"


class ManagerUsersListView(PermissionRequiredMixin, ManagerRequiredMixin, ListView):
    """Список пользователей для управления доступом и блокировки."""

    model = User
    template_name = "users/manager/manager_users_list.html"
    context_object_name = "users"
    paginate_by = 10
    permission_required = "users.can_view_all_users"

    def get_queryset(self):
        return (
            User.objects.filter(is_manager=False)
            .exclude(is_staff=True, is_superuser=True)
            .annotate(
                clients_count=Count("clients", distinct=True),
                mailings_count=Count("mailings", distinct=True),
            )
        )


class ManagerUserDetailView(PermissionRequiredMixin, ManagerRequiredMixin, DetailView):
    """Детальная информация о пользователе с его клиентами и рассылками."""

    model = User
    template_name = "users/manager/manager_user_detail.html"
    context_object_name = "view_user"
    permission_required = "users.can_view_all_users", "users.can_block_users"

    def get_queryset(self):
        return (
            User.objects.filter(is_manager=False)
            .exclude(is_staff=True, is_superuser=True)
            .annotate(
                clients_count=Count("clients", distinct=True),
                mailings_count=Count("mailings", distinct=True),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        context["last_clients"] = Client.objects.filter(owner=user).order_by("-id")[:5]
        context["last_mailings"] = Mailing.objects.filter(owner=user).order_by("-id")[:5]

        return context


def is_manager(user: User) -> bool:
    """Проверяет, является ли пользователь менеджером."""
    return user.is_authenticated and user.is_manager


@permission_required("users.can_block_users", raise_exception=True)
@user_passes_test(is_manager)
@login_required
def manager_toggle_block(request, pk):
    """Переключает статус блокировки пользователя."""
    user_obj = get_object_or_404(
        User.objects.filter(is_manager=False).exclude(is_staff=True, is_superuser=True),
        pk=pk,
    )
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    return redirect("users:manager_user_detail", pk=pk)


class ManagerMailingsListView(PermissionRequiredMixin, ManagerRequiredMixin, ListView):
    """Список всех рассылок в системе для мониторинга менеджером."""

    model = Mailing
    template_name = "users/manager/manager_mailings_list.html"
    context_object_name = "mailings"
    paginate_by = 10
    permission_required = "mailing.can_view_all_mailings"

    def get_queryset(self):
        return Mailing.objects.all().prefetch_related("clients").select_related("message")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailings_qs = self.get_queryset()

        context["total_mailings"] = mailings_qs.count()
        context["started_mailings"] = mailings_qs.filter(status="started").count()
        context["finished_mailings"] = mailings_qs.filter(status="finished").count()

        return context


class ManagerMailingDetailView(PermissionRequiredMixin, ManagerRequiredMixin, DetailView):
    """Детальная информация о рассылке с логами отправки и статистикой."""

    model = Mailing
    template_name = "users/manager/manager_mailing_detail.html"
    context_object_name = "mailing"
    permission_required = ("mailing.can_view_all_mailings", "mailing.can_disable_mailings")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # как и у обычного пользователя — динамически обновляем статус
        obj.update_status()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object
        now = timezone.now()

        # флаги интервала — если захочешь что-то подсвечивать менеджеру
        interval_invalid = mailing.start_time >= mailing.end_time
        before_window = mailing.start_time > now
        after_window = mailing.end_time < now

        logs_qs = MailingLog.objects.filter(mailing=mailing).select_related("client").order_by("-attempt_time")

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
        context["now"] = now

        return context


class ManagerMailingDisableView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Представление для принудительного отключения рассылки менеджером."""

    permission_required = "mailing.can_disable_mailings"

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        mailing.end_time = timezone.now()
        mailing.save(update_fields=["end_time"])
        mailing.update_status()
        messages.success(request, "Рассылка была отключена менеджером.")

        return redirect("users:manager_mailing_detail", pk=mailing.pk)
