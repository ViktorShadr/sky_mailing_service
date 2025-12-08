# Отчёт по восстановлению пароля (Django)

## Краткое состояние
- Пользовательские страницы восстановления пароля и шаблоны лежат в `templates/registration/` и подключены через `users.views.password_reset`.
- Ссылка «Забыли пароль?» в форме логина указывает на `users:password_reset`, совпадает с роутом `users/urls.py`.
- Основная проблема NoReverseMatch происходит из-за отсутствия глобального имени `password_reset_confirm`, которое требуется стандартной логике Django (например, в дефолтных шаблонах или сторонних вызовах `reverse`).

## Детальный разбор (Проблема → Причина → Как исправить)

### 1. Нет глобального URL `password_reset_confirm`
- **Проблема.** Ошибка `Reverse for 'password_reset_confirm' not found` возникает при попытке реверсировать неименованный (без namespace) маршрут.
- **Причина.** В `users/urls.py` роут `password_reset/confirm/<uidb64>/<token>/` объявлен только в namespace `users`, поэтому глобального имени `password_reset_confirm` нет и `reverse('password_reset_confirm')` падает.【F:users/urls.py†L1-L31】【c1626f†L1-L2】
- **Как исправить.**
  - Добавить алиас без namespace в `config/urls.py`, например:
    ```python
    from users.views.password_reset import UserPasswordResetConfirmView
    path("users/password_reset/confirm/<uidb64>/<token>/", UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    ```
  - Либо использовать кастомную форму для PasswordResetView и строить ссылку через `reverse("users:password_reset_confirm", ...)`, исключив обращения к неименованному маршруту.

### 2. Шаблон письма дублирует ссылку и содержит необъявленную переменную
- **Проблема.** В `password_reset_email.html` есть одновременно `{{ url }}` (переменная не приходит из `PasswordResetForm.save`) и URL-тег с namespace, что может путать и приводит к пустой/битой ссылке при использовании `{{ url }}`.【F:templates/registration/password_reset_email.html†L1-L18】
- **Причина.** Контекст стандартной формы не содержит ключа `url`, поэтому первая часть `<a href="{{ protocol }}://{{ domain }}{{ url }}">` рендерится пустой, хотя вторая часть корректна.
- **Как исправить.** Убрать `{{ url }}` и использовать только `{% url 'users:password_reset_confirm' uidb64=uid token=token %}` или добавлять `reset_url` в `extra_email_context`/кастомную форму и подставлять его единообразно.

### 3. Не задан `subject_template_name` и отсутствует пользовательский subject-шаблон
- **Проблема.** `UserPasswordResetView` не переопределяет `subject_template_name`, поэтому берётся дефолтный `registration/password_reset_subject.txt`, которого в проекте нет.
- **Причина.** В репозитории отсутствует `templates/registration/password_reset_subject.txt`, поэтому будет использован встроенный админский шаблон, что не соответствует кастомному UI.
- **Как исправить.** Создать `templates/registration/password_reset_subject.txt` (например, «Сброс пароля на SkyMail») и указать `subject_template_name = "registration/password_reset_subject.txt"` во вьюхе.

### 4. Нет кастомной формы для корректной генерации ссылки в письме
- **Проблема.** Сейчас используется стандартный `PasswordResetForm`, который не знает о namespace `users` и не формирует ссылку в контекст.
- **Причина.** Если где-то используется дефолтный шаблон или кастомные вызовы `reverse('password_reset_confirm')`, возникает несовпадение нейминга.
- **Как исправить.** Создать `UserPasswordResetForm`, переопределить `save` или `get_email_context`, чтобы добавлять `reset_url = reverse("users:password_reset_confirm", ...)`, и указать `form_class = UserPasswordResetForm` в `UserPasswordResetView`.

## Проверка текущего flow
1. **Логин** (`users/templates/users/login.html`) содержит кнопку «Забыли пароль?» с `href="{% url 'users:password_reset' %}` — маршрут существует.【F:users/templates/users/login.html†L14-L23】
2. **Форма ввода email** — `UserPasswordResetView` использует `registration/password_reset_form.html`; success ведёт на `users:password_reset_done` корректно.【F:users/views/password_reset.py†L6-L19】【F:templates/registration/password_reset_form.html†L1-L38】
3. **Письмо** — шаблон найден, но содержит дублирующую ссылку, см. пункт 2 выше.【F:templates/registration/password_reset_email.html†L1-L18】
4. **Подтверждение** — `UserPasswordResetConfirmView` рендерит `registration/password_reset_confirm.html`; success_url ведёт на `users:password_reset_complete`, редиректов по кругу нет.【F:users/views/password_reset.py†L12-L19】【F:templates/registration/password_reset_confirm.html†L1-L36】
5. **Финал** — `password_reset_complete.html` доступен и ссылается на `users:login`.【F:templates/registration/password_reset_complete.html†L1-L18】

## Рекомендации по доведению до продового состояния
- Добавить глобальный алиас `password_reset_confirm` или кастомную форму с namespace-ссылкой, чтобы убрать `NoReverseMatch`.
- Почистить шаблон письма (оставить одну корректную ссылку) и добавить subject-шаблон.
- Во `UserPasswordResetView` явно указать `subject_template_name` и при необходимости `form_class` (кастомная форма выше).
- После правок пройти полный сценарий: логин → «Забыли пароль?» → письмо → форма нового пароля → завершение, убедившись, что URL в письме совпадает с маршрутом.
