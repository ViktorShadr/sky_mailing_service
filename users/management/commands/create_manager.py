from django.core.management import BaseCommand
from django.contrib.auth.models import Group

from users.models import User

MANAGER_GROUP_NAME = "Managers"


class Command(BaseCommand):
    help = "Создание менеджера и добавление его в группу Managers"

    def handle(self, *args, **kwargs):
        email = input("Введите email: ")
        password = input("Введите пароль: ")

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR("Пользователь с таким email уже существует."))
            return

        user = User.objects.create_user(
            email=email,
            password=password,
            is_manager=True,
            is_active=True,
        )

        group, created = Group.objects.get_or_create(name=MANAGER_GROUP_NAME)

        if created:
            self.stdout.write(self.style.WARNING(f"Группа '{MANAGER_GROUP_NAME}' была создана."))

        user.groups.add(group)

        self.stdout.write(
            self.style.SUCCESS(f"Менеджер {user.email} успешно создан и добавлен в группу '{MANAGER_GROUP_NAME}'.")
        )
