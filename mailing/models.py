from django.db import models


class Client(models.Model):
    email = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    comment = models.TextField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField(max_length=255)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Mailing(models.Model):
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255,
                              choices=(('created', 'Создана'), ('started', 'Запущена'), ('finished', 'Завершена')))
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class MailingLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=(('success', 'Успешно'), ('failed', 'Не успешно')))
    server_response = models.TextField(max_length=255)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)

    def __str__(self):
        return self.server_response

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
