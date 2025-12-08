from django import forms
from django.utils import timezone

from .models import Client, Message, Mailing


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ("email", "name", "comment")

        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Введите email"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите ФИО"}),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Комментарий", "rows": 3}
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
        fields = ("message", "clients", "start_time", "end_time")

        widgets = {
            "message": forms.Select(attrs={"class": "form-control"}),
            "clients": forms.SelectMultiple(attrs={"class": "form-control"}),
            "start_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        }

        labels = {
            "message": "Сообщение",
            "clients": "Получатели",
            "start_time": "Дата и время начала",
            "end_time": "Дата и время окончания",
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        now = timezone.now()

        if start_time and start_time < now:
            self.add_error("start_time", "Дата начала рассылки не может быть в прошлом.")

        if start_time and end_time and start_time >= end_time:
            self.add_error("end_time", "Дата окончания рассылки должна быть позже даты начала.")

        return cleaned_data

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            # Показываем только сообщения текущего пользователя
            self.fields["message"].queryset = Message.objects.filter(owner=user)

            # Показываем только клиентов текущего пользователя
            self.fields["clients"].queryset = Client.objects.filter(owner=user)
