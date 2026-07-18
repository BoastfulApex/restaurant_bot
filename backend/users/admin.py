from django.contrib import admin
from .models import BotUser


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'username', 'phone', 'telegram_id', 'created_at']
    search_fields = ['full_name', 'username', 'phone', 'telegram_id']
    ordering = ['-created_at']
    list_per_page = 20
    readonly_fields = ['telegram_id', 'created_at']
