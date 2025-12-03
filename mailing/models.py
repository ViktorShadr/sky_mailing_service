from django.db import models
from django.utils import timezone

from users.models import User


class Client(models.Model):
    email = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    comment = models.TextField(max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="clients", verbose_name="Владелец клиента"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        permissions = [
            ("mailing.view_client", "Может просматривать клиентов"),
            ("mailing.add_client", "Может добавлять клиентов"),
            ("mailing.change_client", "Может редактировать клиентов"),
            ("mailing.delete_client", "Может удалять клиентов"),
        ]


class Message(models.Model):
    subject = models.CharField("Тема", max_length=255)
    body = models.TextField("Тело письма", max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="messages",
        verbose_name="Владелец сообщения"
    )

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    start_time = models.DateTimeField("Дата и время начала отправки")
    end_time = models.DateTimeField("Дата и время окончания отправки")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="mailings", verbose_name="Владелец рассылки"
    )

    status = models.CharField(
        max_length=20,
        choices=(
            ("created", "Создана"),
            ("started", "Запущена"),
            ("finished", "Завершена"),
        ),
        default="created",
    )

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)

    def update_status(self, save=True):
        """Пересчитывает статус на основе текущего времени и интервала."""
        now = timezone.now()

        if now < self.start_time:
            new_status = "created"
        elif self.start_time <= now <= self.end_time:
            new_status = "started"
        else:
            new_status = "finished"

        if new_status != self.status:
            self.status = new_status
            if save:
                self.save(update_fields=["status"])

    def __str__(self):
        return f"{self.message.subject} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("mailing.view_mailing", "Может просматривать рассылки"),
            ("mailing.add_mailing", "Может добавлять рассылки"),
            ("mailing.change_mailing", "Может редактировать рассылки"),
            ("mailing.delete_mailing", "Может удалять рассылки"),
        ]


class MailingLog(models.Model):
    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=(("success", "Успешно"), ("failed", "Не успешно")))
    server_response = models.TextField()
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)

    def __str__(self):
        return self.server_response

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
