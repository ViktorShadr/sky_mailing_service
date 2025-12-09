from django.core.management import BaseCommand, call_command

from mailing.models import Client, Mailing, MailingLog, Message
from users.models import User


class Command(BaseCommand):
    help = "Load test data from fixtures"

    def handle(self, *args, **kwargs):
        Client.objects.all().delete()
        Message.objects.all().delete()
        Mailing.objects.all().delete()
        MailingLog.objects.all().delete()
        User.objects.all().delete()
        call_command("loaddata", "users_test.json")
        call_command("loaddata", "mailing_test.json")

        self.stdout.write(self.style.SUCCESS("Successfully loaded data from fixture"))
