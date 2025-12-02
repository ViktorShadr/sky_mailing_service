from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from mailing.models import Mailing


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = 6

    def get_queryset(self):
        return Mailing.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_mailings"] = Mailing.objects.count()
        context["started_mailings"] = Mailing.objects.filter(status="started").count()
        context["finished_mailings"] = Mailing.objects.filter(status="finished").count()
        return context