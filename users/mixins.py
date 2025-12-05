from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from users.models import User


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Доступ только для менеджеров.
    """

    def test_func(self):
        user: User = self.request.user
        return user.is_authenticated and user.is_manager

    def handle_no_permission(self):
        raise PermissionDenied
