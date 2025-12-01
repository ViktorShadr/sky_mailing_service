from django.urls import path

from mailing.views import MailingTemplateView, RecipientListView

app_name = 'mailing'

urlpatterns = [
    path('', MailingTemplateView.as_view(), name='index'),
    path('recipient/', RecipientListView.as_view(), name='recipient'),
    # path('message/', MessageTemplateView.as_view(), name='message'),
    # path('mailing/', MailingListTemplateView.as_view(), name='mailing'),
]