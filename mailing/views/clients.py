from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from mailing.forms import ClientForm
from mailing.models import Client


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_clients"):
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("mailing:client_list")


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        client = self.get_object()
        user = request.user

        if client.owner == user:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user

        is_owner = self.object.owner == user

        if is_owner:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied
