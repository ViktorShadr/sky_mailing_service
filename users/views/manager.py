from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from mailing.models import Mailing
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



