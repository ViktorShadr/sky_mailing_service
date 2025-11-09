from django.views.generic import TemplateView


class MailingTemplateView(TemplateView):
    template_name = "mailing/index.html"


