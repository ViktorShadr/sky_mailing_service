from django import forms

from .models import Client, Message, Mailing


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ("email", "name", "comment")

        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Введите email"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите ФИО"}),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Комментарий (опционально)", "rows": 3}
            ),
        }

        labels = {
            "email": "Email",
            "name": "ФИО",
            "comment": "Комментарий",
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("subject", "body")

        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите тему"}),
            "body": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Введите текст сообщения", "rows": 3}
            ),
        }

        labels = {
            "subject": "Тема",
            "body": "Текст сообщения",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ("message", "clients", "start_time", "end_time", "status")

        widgets = {
            "message": forms.Select(attrs={"class": "form-control"}),
            "clients": forms.SelectMultiple(attrs={"class": "form-control"}),
            "start_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

        labels = {
            "message": "Сообщение",
            "clients": "Получатели",
            "start_time": "Дата и время начала",
            "end_time": "Дата и время окончания",
            "status": "Статус",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            # Показываем только сообщения текущего пользователя
            self.fields["message"].queryset = Message.objects.filter(owner=user)

            # Показываем только клиентов текущего пользователя
            self.fields["clients"].queryset = Client.objects.filter(owner=user)
