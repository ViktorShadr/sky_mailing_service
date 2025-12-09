import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Mailing, MailingLog

logger = logging.getLogger("mailing")


def run_mailing(mailing: Mailing) -> dict:
    """
    Выполняет рассылку сообщения указанным клиентам.
    Возвращает словарь с результатами выполнения рассылки.
    """
    logger.info("Запуск рассылки id=%s", mailing.id)
    now = timezone.now()

    if mailing.start_time >= mailing.end_time:
        return {
            "ok": False,
            "error": (
                "Интервал рассылки задан некорректно: "
                "дата окончания должна быть позже даты начала.\n"
                f"Начало: {mailing.start_time.strftime('%d.%m.%Y %H:%M')}, "
                f"окончание: {mailing.end_time.strftime('%d.%m.%Y %H:%M')}."
            ),
            "total": 0,
            "success": 0,
            "failed": 0,
        }

    if not (mailing.start_time <= now <= mailing.end_time):
        return {
            "ok": False,
            "error": (
                "Текущее время не входит в интервал рассылки.\n"
                f"Сейчас: {now.strftime('%d.%m.%Y %H:%M')}, "
                f"интервал: с {mailing.start_time.strftime('%d.%m.%Y %H:%M')} "
                f"по {mailing.end_time.strftime('%d.%m.%Y %H:%M')}."
            ),
            "total": 0,
            "success": 0,
            "failed": 0,
        }

    mailing.update_status()

    clients = mailing.clients.all()
    total = clients.count()
    logger.info("Рассылка id=%s: найдено %s получателей", mailing.id, total)
    success_count = 0
    failed_count = 0

    subject = mailing.message.subject
    body = mailing.message.body
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

    for client in clients:
        try:
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[client.email],
                fail_silently=False,
            )
        except Exception as exc:
            failed_count += 1
            logger.error(
                "Ошибка при отправке письма: mailing_id=%s, client_id=%s, error=%s",
                mailing.id,
                client.id,
                str(exc),
                exc_info=True,
            )
            MailingLog.objects.create(
                mailing=mailing,
                client=client,
                status="failed",
                server_response=str(exc),
            )
        else:
            if sent == 1:
                success_count += 1
                logger.info(
                    "Письмо успешно отправлено: mailing_id=%s, client_id=%s",
                    mailing.id,
                    client.id,
                )
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status="success",
                    server_response="OK (send_mail returned 1)",
                )
            else:
                failed_count += 1
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status="failed",
                    server_response=f"send_mail returned {sent}",
                )

    mailing.update_status()

    return {
        "ok": True,
        "error": "",
        "total": total,
        "success": success_count,
        "failed": failed_count,
    }
