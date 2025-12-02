from django.urls import path

from mailing.views.clients import ClientListView, ClientUpdateView, ClientDeleteView, ClientCreateView
from mailing.views.mailings import MailingListView
from mailing.views.main import MailingTemplateView
from mailing.views.messages import MessageListView, MessageUpdateView, MessageDeleteView, MessageCreateView

app_name = 'mailing'

urlpatterns = [
    path('', MailingTemplateView.as_view(), name='index'),
    path('client/', ClientListView.as_view(), name='client_list'),
    path('client/<int:pk>/', ClientUpdateView.as_view(), name='client_update'),
    path('client/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('client/create/', ClientCreateView.as_view(), name='client_create'),
    path('message/', MessageListView.as_view(), name='message_list'),
    path('message/<int:pk>/', MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('message/create/', MessageCreateView.as_view(), name='message_create'),
    path('mailing/', MailingListView.as_view(), name='mailing'),
]
