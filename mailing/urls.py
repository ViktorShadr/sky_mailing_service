from django.urls import path

from mailing.views import MailingTemplateView

app_name = 'mailing'

urlpatterns = [
    path('', MailingTemplateView.as_view(), name='index'),
]