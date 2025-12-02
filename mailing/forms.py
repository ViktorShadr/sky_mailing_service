from django import forms

from .models import Client, Message


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('email', 'name', 'comment')

        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ФИО'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Комментарий (опционально)',
                'rows': 3
            }),
        }

        labels = {
            'email': 'Email',
            'name': 'ФИО',
            'comment': 'Комментарий',
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('subject', 'body')

        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите тему'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите текст сообщения',
                'rows': 3
            }),
        }
