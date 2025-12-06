from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

MANAGER_GROUP_NAME = "Managers"

PERMISSIONS = [
    "can_view_all_users",
    "can_block_users",

    "can_view_all_mailings",
    "can_disable_mailings",

    "can_view_all_clients",
]


class Command(BaseCommand):
    help = "Создаёт группу Managers и назначает ей необходимые пермишены"

    def handle(self, *args, **options):

        group, created = Group.objects.get_or_create(name=MANAGER_GROUP_NAME)

        if created:
            self.stdout.write(self.style.SUCCESS(f"Группа '{MANAGER_GROUP_NAME}' создана."))
        else:
            self.stdout.write(self.style.WARNING(f"Группа '{MANAGER_GROUP_NAME}' уже существует."))

        added = 0
        for codename in PERMISSIONS:
            try:
                perm = Permission.objects.get(codename=codename)
                group.permissions.add(perm)
                added += 1
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Permission '{codename}' не найден!"))

        group.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Назначено прав: {added}. Группа '{MANAGER_GROUP_NAME}' готова."
            )
        )
