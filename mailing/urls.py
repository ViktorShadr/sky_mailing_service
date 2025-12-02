from django.urls import path

from mailing.views import MailingTemplateView, RecipientListView, MessageListView, MailingListView

app_name = 'mailing'

urlpatterns = [
    path('', MailingTemplateView.as_view(), name='index'),
    path('recipient/', RecipientListView.as_view(), name='recipient'),
    path('message/', MessageListView.as_view(), name='message'),
    path('mailing/', MailingListView.as_view(), name='mailing'),
]