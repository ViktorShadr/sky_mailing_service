from django.urls import path

from users.views.user import CustomLoginView, CustomLogoutView, CustomRegistrationView, RegistrationDoneView, \
    ConfirmEmailView, ProfileDetailView, ProfileUpdateView, ProfileDeleteView
from users.views.manager import ManagerDashboardView

app_name = "users"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("registration/", CustomRegistrationView.as_view(), name="registration"),
    path("registration/done/", RegistrationDoneView.as_view(), name="registration_done"),
    path("confirm_email/<uidb64>/<token>/", ConfirmEmailView.as_view(), name="confirm_email"),
    path("profile/", ProfileDetailView.as_view(), name="profile_detail"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path("profile/delete/", ProfileDeleteView.as_view(), name="profile_delete"),
    path("manager/", ManagerDashboardView.as_view(), name="manager_dashboard"),
]
