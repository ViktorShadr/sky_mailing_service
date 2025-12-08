from django.urls import path

from mailing.views.clients import ClientCreateView, ClientDeleteView, ClientListView, ClientUpdateView
from mailing.views.mailing_logs import MailingLogListView
from mailing.views.mailings import (
    MailingListView,
    MailingUpdateView,
    MailingDeleteView,
    MailingCreateView,
    MailingRunView,
    MailingDetailView,
)
from mailing.views.main import MailingTemplateView
from mailing.views.messages import MessageCreateView, MessageDeleteView, MessageListView, MessageUpdateView

app_name = "mailing"

urlpatterns = [
    path("", MailingTemplateView.as_view(), name="index"),
    path("client/", ClientListView.as_view(), name="client_list"),
    path("client/<int:pk>/", ClientUpdateView.as_view(), name="client_update"),
    path("client/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("client/create/", ClientCreateView.as_view(), name="client_create"),
    path("message/", MessageListView.as_view(), name="message_list"),
    path("message/<int:pk>/", MessageUpdateView.as_view(), name="message_update"),
    path("message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path("mailing/", MailingListView.as_view(), name="mailing_list"),
    path("mailing/<int:pk>/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailing/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>/run/", MailingRunView.as_view(), name="mailing_run"),
    path("mailing/<int:pk>/detail/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/log/", MailingLogListView.as_view(), name="mailing_log"),
]
