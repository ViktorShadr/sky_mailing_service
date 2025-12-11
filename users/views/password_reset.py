from django.contrib.auth.views import (PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import reverse_lazy

from users.forms import UserSetPasswordForm


class UserPasswordResetView(PasswordResetView):
    """Отображает и обрабатывает форму запроса сброса пароля."""

    template_name = "registration/password_reset_form.html"

    email_template_name = "registration/password_reset_email.txt"
    html_email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("users:password_reset_done")


class UserPasswordResetDoneView(PasswordResetDoneView):
    """Отображает страницу подтверждения отправки письма для сброса пароля."""

    template_name = "registration/password_reset_done.html"


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    """Обрабатывает форму установки нового пароля по ссылке из письма."""

    template_name = "registration/password_reset_confirm.html"
    form_class = UserSetPasswordForm
    success_url = reverse_lazy("users:password_reset_complete")


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    """Отображает страницу успешного сброса пароля."""

    template_name = "registration/password_reset_complete.html"
