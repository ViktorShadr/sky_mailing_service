from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing
from mailing.services import run_mailing


class Command(BaseCommand):
    help = "Запускает все рассылки, чей временной интервал включает текущее время."

    def handle(self, *args, **options):
        now = timezone.now()

        mailings = (
            Mailing.objects.filter(start_time__lte=now, end_time__gte=now)
            .exclude(status="finished")
            .select_related("message")
            .prefetch_related("clients")
        )

        if not mailings.exists():
            self.stdout.write(self.style.WARNING("Нет рассылок, доступных для отправки."))
            return

        for mailing in mailings:
            mailing.update_status()

            try:
                result = run_mailing(mailing)
            except Exception as exc:  # pragma: no cover - защита от неожиданных сбоев
                self.stdout.write(
                    self.style.ERROR(
                        f"Рассылка #{mailing.pk} завершилась с ошибкой исполнения: {exc}"
                    )
                )
                continue

            if result.get("ok"):
                self.stdout.write(
                    self.style.SUCCESS(
                        (
                            f"Рассылка #{mailing.pk} отправлена: всего {result['total']}, "
                            f"успешно {result['success']}, ошибок {result['failed']}."
                        )
                    )
                )
            else:
                error_message = result.get("error", "Неизвестная ошибка")
                self.stdout.write(
                    self.style.ERROR(f"Рассылка #{mailing.pk} не запущена: {error_message}")
                )
