from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.core.mail import send_mail
import os
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from .models import User


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    form_class = UserLoginForm


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("mailing:index")


class CustomRegistrationView(CreateView):
    template_name = "users/registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = 'Добро пожаловать в наш магазин'
        message = 'Спасибо, что зарегистрировались в SkySport!'
        recipient_list = [user_email]
        send_mail(subject, message, from_email=os.getenv('FROM_EMAIL'), recipient_list=recipient_list)


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
