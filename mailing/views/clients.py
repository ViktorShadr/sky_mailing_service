from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from mailing.forms import ClientForm
from mailing.mixins import OwnerAccessMixin, OwnerQuerysetMixin
from mailing.models import Client


class ClientListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"
    paginate_by = 6


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("mailing:client_list")


class ClientUpdateView(LoginRequiredMixin, OwnerAccessMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"

    def get_success_url(self):
        return reverse_lazy("mailing:client_detail", kwargs={"pk": self.object.pk})


class ClientDetailView(LoginRequiredMixin, OwnerAccessMixin, DetailView):
    model = Client
    template_name = "mailing/client_detail.html"
    context_object_name = "client"


class ClientDeleteView(LoginRequiredMixin, OwnerAccessMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")
