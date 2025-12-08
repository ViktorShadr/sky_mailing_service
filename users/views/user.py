import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView

from config import settings
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from users.models import User


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    form_class = UserLoginForm


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("mailing:index")


class CustomRegistrationView(CreateView):
    template_name = "users/registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:registration_done")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        self.send_confirmation_email(user)
        return response

    def send_confirmation_email(self, user):
        """
        Отправка письма со ссылкой для подтверждения email.
        """
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        confirm_url = self.request.build_absolute_uri(
            reverse("users:confirm_email", kwargs={"uidb64": uidb64, "token": token})
        )

        context = {
            "user": user,
            "confirm_url": confirm_url,
            "site_name": "SkyMail",
        }

        subject = render_to_string(
            "users/email/registration_confirm_subject.txt", context
        ).strip()

        message = render_to_string(
            "users/email/registration_confirm_email.txt", context
        )

        html_message = render_to_string(
            "users/email/registration_confirm_email.html", context
        )

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", os.getenv("FROM_EMAIL"))

        send_mail(
            subject,
            message,
            from_email,
            [user.email],
            html_message=html_message,
        )


class RegistrationDoneView(TemplateView):
    template_name = "users/registration_done.html"


class ConfirmEmailView(TemplateView):
    template_name = "users/confirm_email.html"

    def get_success_url(self):
        return reverse("users:login") + "?email_confirmed=1"

    def get(self, request, *args, **kwargs):
        uidb64 = kwargs.get("uidb64")
        token = kwargs.get("token")

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect(self.get_success_url())
        else:
            return TemplateResponse(request, "users/confirm_email_invalid.html", {})


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile_detail.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile_form.html"
    success_url = reverse_lazy("users:profile_detail")

    def get_object(self, queryset=None):
        return self.request.user


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "users/profile_confirm_delete.html"
    success_url = reverse_lazy("mailing:index")

    def get_object(self, queryset=None):
        return self.request.user
