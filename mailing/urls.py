from django.urls import path

from mailing.views import MailingTemplateView

urlpatterns = [
    path('', MailingTemplateView.as_view(), name='index'),
]