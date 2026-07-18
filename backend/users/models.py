from django.db import models


class BotUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    full_name = models.CharField(max_length=200, blank=True, verbose_name="Ismi")
    username = models.CharField(max_length=100, blank=True, verbose_name="Username")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon raqami")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ro'yxatdan o'tgan vaqti")

    class Meta:
        verbose_name = "Bot foydalanuvchisi"
        verbose_name_plural = "Bot foydalanuvchilari"
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name or self.username or str(self.telegram_id)
