from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect

from mailing.models import Mailing, Client
from users.models import User


class ManagerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "users/manager/manager_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Берём только обычных пользователей, без админов
        users_qs = User.objects.exclude(is_staff=True, is_superuser=True)

        context["total_users"] = users_qs.count()
        context["blocked_users"] = users_qs.filter(is_active=False).count()
        context["active_users"] = users_qs.filter(is_active=True).count()

        mailings_qs = Mailing.objects.all()
        context["total_mailings"] = mailings_qs.count()

        # Логику можно подправить под твои статусы.
        # Здесь считаем активными "started", а остальное считаем отключённым/неактивным.
        context["active_mailings"] = mailings_qs.filter(status="started").count()
        context["disabled_mailings"] = mailings_qs.exclude(status="started").count()

        return context


class ManagerClientsListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "users/manager/manager_clients_list.html"
    context_object_name = "clients"
    paginate_by = 10

    def get_queryset(self):
        # Менеджер видит всех клиентов сервиса
        return Client.objects.select_related("owner").all()


class ManagerUsersListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/manager/manager_users_list.html"
    context_object_name = "users"
    paginate_by = 10

    def get_queryset(self):
        return (
            User.objects
            .exclude(is_staff=True, is_superuser=True)
            .annotate(
                clients_count=Count("clients", distinct=True),
                mailings_count=Count("mailings", distinct=True),
            )
        )


class ManagerMailingsListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "users/manager/manager_mailings_list.html"
    context_object_name = "mailings"
    paginate_by = 10

    def get_queryset(self):
        # Менеджер видит все рассылки
        return Mailing.objects.all().prefetch_related("clients", "message")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailings_qs = self.object_list

        context["total_mailings"] = mailings_qs.count()
        context["started_mailings"] = mailings_qs.filter(status="started").count()
        context["finished_mailings"] = mailings_qs.filter(status="finished").count()

        return context


class ManagerUserDetailView(LoginRequiredMixin, DetailView):
    """
    Карточка одного пользователя под шаблон manager_user_detail.html
    """
    model = User
    template_name = "users/manager/manager_user_detail.html"
    context_object_name = "view_user"

    def get_queryset(self):
        # Тот же базовый queryset, что и в списке, со счётчиками
        return (
            User.objects
            .exclude(is_staff=True, is_superuser=True)
            .annotate(
                clients_count=Count("clients", distinct=True),
                mailings_count=Count("mailings", distinct=True),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        context["last_clients"] = (
            Client.objects.filter(owner=user).order_by("-id")[:5]
        )
        context["last_mailings"] = (
            Mailing.objects.filter(owner=user).order_by("-id")[:5]
        )

        return context


def manager_toggle_block(request, pk):
    """
    Переключение блокировки пользователя.
    Подключи эту вьюху к урлу 'users:manager_toggle_block'.
    """
    # Здесь можно добавить проверку, что текущий юзер — менеджер
    user = get_object_or_404(
        User.objects.exclude(is_staff=True, is_superuser=True),
        pk=pk,
    )
    user.is_active = not user.is_active
    user.save()
    return redirect("users:manager_user_detail", pk=pk)
