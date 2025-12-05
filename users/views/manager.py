from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView

from mailing.models import Mailing, Client
from users.mixins import ManagerRequiredMixin
from users.models import User


class ManagerDashboardView(ManagerRequiredMixin, TemplateView):
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


class ManagerClientsListView(ManagerRequiredMixin, ListView):
    model = Client
    template_name = "users/manager/manager_clients_list.html"
    context_object_name = "clients"
    paginate_by = 10

    def get_queryset(self):
        # Менеджер видит всех клиентов сервиса
        return Client.objects.select_related("owner").all()


class ManagerUsersListView(ManagerRequiredMixin, ListView):
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


class ManagerMailingsListView(ManagerRequiredMixin, ListView):
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

    def post(self, request, *args, **kwargs):
        mailing_id = request.POST.get("mailing_id")
        action = request.POST.get("action")

        if mailing_id and action:
            mailing = Mailing.objects.get(pk=mailing_id)

            # Отключение
            if action == "disable" and mailing.status == "started":
                mailing.status = "finished"  # или "disabled", если есть такой статус
                mailing.save()

            # Включение
            elif action == "enable" and mailing.status in ("created", "finished"):
                mailing.status = "started"
                mailing.save()

        # После выполнения — возвращаемся на список
        return redirect("users:manager_mailings_list")


class ManagerUserDetailView(ManagerRequiredMixin, DetailView):
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


def is_manager(user: User) -> bool:
    return user.is_authenticated and user.is_manager


@user_passes_test(is_manager)
@login_required
def manager_toggle_block(request, pk):
    user_obj = get_object_or_404(
        User.objects.exclude(is_staff=True, is_superuser=True),
        pk=pk,
    )
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    return redirect("users:manager_user_detail", pk=pk)
