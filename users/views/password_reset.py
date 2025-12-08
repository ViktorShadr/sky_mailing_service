from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy, reverse

from users.forms import UserSetPasswordForm


class UserPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset_form.html"

    email_template_name = "registration/password_reset_email.txt"
    html_email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("users:password_reset_done")


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    form_class = UserSetPasswordForm
    success_url = reverse_lazy("users:password_reset_complete")


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
