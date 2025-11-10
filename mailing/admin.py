from django.contrib import admin
from .models import Client, Mailing, MailingLog, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'comment')
    search_fields = ('email', 'name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body')
    search_fields = ('subject',)


class MailingLogInline(admin.TabularInline):
    model = MailingLog
    extra = 0
    readonly_fields = ('date', 'status', 'server_response')
    can_delete = False


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('date_start', 'date_end', 'status', 'message', 'clients_list')
    list_filter = ('status',)
    search_fields = ('message__subject',)
    filter_horizontal = ('clients',)
    inlines = [MailingLogInline]

    def clients_list(self, obj):
        return ", ".join([client.email for client in obj.clients.all()])

    clients_list.short_description = 'Клиенты'


@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'status', 'server_response', 'mailing')
    list_filter = ('status',)
