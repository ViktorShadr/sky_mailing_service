from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView

from mailing.models import Mailing, Client
from users.models import User


class ManagerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "users/manager/manager_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_users"] = User.objects.count()
        context["blocked_users"] = User.objects.filter(is_active=False).count()
        context["active_users"] = User.objects.filter(is_active=True).count()
        context["total_mailings"] = Mailing.objects.count()
        context["active_mailings"] = Mailing.objects.filter(status="active").count()
        context["disabled_mailings"] = Mailing.objects.filter(status="disabled").count()
        return context


class ManagerClientsListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/manager/manager_clients_list.html"
    context_object_name = "clients"
    paginate_by = 10

    def get_queryset(self):
        return Client.objects.all()


class ManagerUsersListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/manager/manager_users_list.html"
    context_object_name = "users"
    paginate_by = 10

    def get_queryset(self):
        return User.objects.all().exclude(is_staff=True, is_superuser=True)


class ManagerMailingsListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "users/manager/manager_mailings_list.html"
    context_object_name = "mailings"
    paginate_by = 10

    def get_queryset(self):
        return Mailing.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_mailings"] = Mailing.objects.count()
        context["active_mailings"] = Mailing.objects.filter(status="active").count()
        context["disabled_mailings"] = Mailing.objects.filter(status="disabled").count()
        return context
