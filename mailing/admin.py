from django.contrib import admin

from .models import Client, Mailing, MailingLog, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'comment')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body')

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('date_start', 'date_end', 'status', 'message')

@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'status', 'server_response', 'mailing')


