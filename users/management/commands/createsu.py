from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Create superuser"

    def handle(self, *args, **kwargs):
        email = "admin@admin.com"
        password = "admin"

        if User.objects.filter(email=email).exists():
            self.stdout.write("Superuser already exists")
            return

        user = User.objects.create_superuser(email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser created: {user.email}"))
