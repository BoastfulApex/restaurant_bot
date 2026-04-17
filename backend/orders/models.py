from django.db import models
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', '🆕 Yangi'),
        ('confirmed', '✅ Qabul qilindi'),
        ('cooking', '👨‍🍳 Tayyorlanmoqda'),
        ('delivering', '🚗 Yetkazilmoqda'),
        ('done', '✔️ Bajarildi'),
        ('cancelled', '❌ Bekor qilindi'),
    ]

    telegram_id = models.BigIntegerField(verbose_name="Telegram ID")
    full_name = models.CharField(max_length=200, verbose_name="Ism")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    address = models.TextField(blank=True, verbose_name="Manzil (matn)")
    latitude = models.FloatField(null=True, blank=True, verbose_name="Kenglik")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Uzunlik")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Status")
    total_price = models.PositiveIntegerField(verbose_name="Jami narx")
    note = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vaqt")

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} — {self.full_name} ({self.get_status_display()})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # snapshot
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Buyurtma elementi"
        verbose_name_plural = "Buyurtma elementlari"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
