from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создание менеджера"

    def handle(self, *args, **kwargs):
        email = input("Введите email: ")
        password = input("Введите пароль: ")

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR("Пользователь с таким email уже существует."))
            return

        user = User.objects.create_user(email=email, password=password, is_manager=True, is_active=True)
        self.stdout.write(self.style.SUCCESS(f"Менеджер {user.email} успешно создан."))

