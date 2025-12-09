from django.urls import path

from mailing.views.clients import (
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientUpdateView,
)
from mailing.views.mailing_logs import MailingLogListView
from mailing.views.mailings import (
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingRunView,
    MailingUpdateView,
)
from mailing.views.main import MailingTemplateView
from mailing.views.messages import (
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
)

app_name = "mailing"

urlpatterns = [
    path("", MailingTemplateView.as_view(), name="index"),
    path("client/", ClientListView.as_view(), name="client_list"),
    path("client/<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("client/<int:pk>/update/", ClientUpdateView.as_view(), name="client_update"),
    path("client/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("client/create/", ClientCreateView.as_view(), name="client_create"),
    path("message/", MessageListView.as_view(), name="message_list"),
    path("message/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path("mailing/", MailingListView.as_view(), name="mailing_list"),
    path("mailing/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailing/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>/run/", MailingRunView.as_view(), name="mailing_run"),
    path("mailing/log/", MailingLogListView.as_view(), name="mailing_log"),
]
