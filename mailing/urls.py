from django.urls import path

from mailing.templates.mailing.views.clients import ClientListView
from mailing.templates.mailing.views.mailings import MailingListView
from mailing.templates.mailing.views.main import MailingTemplateView
from mailing.templates.mailing.views.messages import MessageListView

app_name = 'mailing'

urlpatterns = [
    path('', MailingTemplateView.as_view(), name='index'),
    path('recipient/', ClientListView.as_view(), name='recipient'),
    path('message/', MessageListView.as_view(), name='message'),
    path('mailing/', MailingListView.as_view(), name='mailing'),
]