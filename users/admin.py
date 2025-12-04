from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "country", "phone", "is_manager")
    list_filter = ("is_manager", "is_superuser", "is_active", "groups")
    search_fields = ("email",)
    ordering = ("email",)
