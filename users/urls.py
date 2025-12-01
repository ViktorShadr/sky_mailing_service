from django.urls import path

from users.views import CustomLoginView, CustomLogoutView, CustomRegistrationView, ProfileDetailView, ProfileUpdateView, \
    ProfileDeleteView, RegistrationDoneView, ConfirmEmailView

app_name = 'users'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('registration/', CustomRegistrationView.as_view(), name='registration'),
    path('registration/done/', RegistrationDoneView.as_view(), name='registration_done'),
    path('confirm_email/<uidb64>/<token>/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('profile/', ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/delete/', ProfileDeleteView.as_view(), name='profile_delete'),
]
