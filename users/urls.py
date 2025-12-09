from django.urls import path

from users.views.manager import (
    ManagerClientDetailView,
    ManagerClientsListView,
    ManagerDashboardView,
    ManagerMailingDetailView,
    ManagerMailingDisableView,
    ManagerMailingsListView,
    ManagerUserDetailView,
    ManagerUsersListView,
    manager_toggle_block,
)
from users.views.password_reset import (
    UserPasswordResetCompleteView,
    UserPasswordResetConfirmView,
    UserPasswordResetDoneView,
    UserPasswordResetView,
)
from users.views.user import (
    ConfirmEmailView,
    CustomLoginView,
    CustomLogoutView,
    CustomRegistrationView,
    ProfileDeleteView,
    ProfileDetailView,
    ProfileUpdateView,
    RegistrationDoneView,
)

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
    path("manager/clients/", ManagerClientsListView.as_view(), name="manager_clients_list"),
    path("manager/client/<int:pk>/", ManagerClientDetailView.as_view(), name="manager_client_detail"),
    path("manager/users/", ManagerUsersListView.as_view(), name="manager_users_list"),
    path("manager/mailings/", ManagerMailingsListView.as_view(), name="manager_mailings_list"),
    path("manager/mailing/<int:pk>/", ManagerMailingDetailView.as_view(), name="manager_mailing_detail"),
    path("manager/mailing/<int:pk>/disable/", ManagerMailingDisableView.as_view(), name="manager_mailing_disable"),
    path("manager/user/<int:pk>/", ManagerUserDetailView.as_view(), name="manager_user_detail"),
    path("manager/user/<int:pk>/toggle_block/", manager_toggle_block, name="manager_toggle_block"),
    path("password_reset/", UserPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", UserPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "password_reset/confirm/<uidb64>/<token>/",
        UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password_reset/complete/", UserPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
