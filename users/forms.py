from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm, PasswordResetForm
from django.urls import reverse

from users.models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите ваш email",
            }
        ),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите пароль",
            }
        ),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Повторите пароль",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован")
        return email

    def save(self, commit=True):
        """
        Создаём пользователя неактивным, чтобы он не мог войти
        до подтверждения email
        """
        user = super().save(commit=False)
        user.is_active = False
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите ваш email",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите пароль",
            }
        ),
    )


class UserProfileForm(forms.ModelForm):
    delete_avatar = forms.BooleanField(
        required=False,
        label="Удалить аватар",
        help_text="Отметьте, чтобы удалить текущий аватар",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = User
        fields = ("avatar", "phone")
        widgets = {
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Не показываем поле delete_avatar, если у пользователя нет аватара
        if not self.instance.avatar:
            self.fields.pop("delete_avatar", None)

    def save(self, commit=True):
        # Если отмечено удаление аватара, удаляем файл и очищаем поле
        if self.cleaned_data.get("delete_avatar"):
            # Удаляем файл аватара, если он существует
            if self.instance.avatar:
                self.instance.avatar.delete(save=False)
            # Очищаем поле аватара
            self.instance.avatar = None

        return super().save(commit)


class UserSetPasswordForm(SetPasswordForm):
    """
    Кастомная форма для установки нового пароля в стиле проекта.
    Используется в UserPasswordResetConfirmView.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Общие атрибуты для всех полей
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")

        # Кастомные лейблы и плейсхолдеры
        self.fields["new_password1"].label = "Новый пароль"
        self.fields["new_password1"].widget.attrs.setdefault("placeholder", "Введите новый пароль")

        self.fields["new_password2"].label = "Подтверждение пароля"
        self.fields["new_password2"].widget.attrs.setdefault("placeholder", "Повторите новый пароль")
