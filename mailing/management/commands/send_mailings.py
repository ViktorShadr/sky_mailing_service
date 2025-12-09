import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing
from mailing.services import run_mailing

logger = logging.getLogger("mailing")


class Command(BaseCommand):
    help = "Запускает все рассылки, чей временной интервал включает текущее время."

    def handle(self, *args, **options):
        logger.info("Старт выполнения management-команды send_mailings")
        now = timezone.now()

        mailings = (
            Mailing.objects.filter(start_time__lte=now, end_time__gte=now)
            .exclude(status="finished")
            .select_related("message")
            .prefetch_related("clients")
        )

        mailings_count = mailings.count()
        logger.info("Найдено рассылок для отправки: %s", mailings_count)

        if mailings_count == 0:
            self.stdout.write(self.style.WARNING("Нет рассылок, доступных для отправки."))
            return

        processed = 0
        errors = 0

        for mailing in mailings:
            processed += 1
            mailing.update_status()

            try:
                result = run_mailing(mailing)
            except Exception as exc:  # pragma: no cover - защита от неожиданных сбоев
                self.stdout.write(self.style.ERROR(f"Рассылка #{mailing.pk} завершилась с ошибкой исполнения: {exc}"))
                errors += 1
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
                self.stdout.write(self.style.ERROR(f"Рассылка #{mailing.pk} не запущена: {error_message}"))
                errors += 1

        logger.info(
            "Итоги выполнения send_mailings: обработано %s, ошибок %s",
            processed,
            errors,
        )
