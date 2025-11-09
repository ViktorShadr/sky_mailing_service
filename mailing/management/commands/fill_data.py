from django.core.management import BaseCommand, call_command

from mailing.models import Client, Message, Mailing, MailingLog


class Command(BaseCommand):
    help = "Load test data from fixtures"

    def handle(self, *args, **kwargs):
        Client.objects.all().delete()
        Message.objects.all().delete()
        Mailing.objects.all().delete()
        MailingLog.objects.all().delete()
        call_command("loaddata", "client_fixture.json")
        call_command("loaddata", "message_fixture.json")
        call_command("loaddata", "mailing_fixture.json")
        call_command("loaddata", "mailing_log_fixture.json")
        self.stdout.write(self.style.SUCCESS("Successfully loaded data from fixture"))