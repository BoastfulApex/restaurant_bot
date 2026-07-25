from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nomi")
    image = models.ImageField(upload_to='categories/', blank=True, verbose_name="Rasm")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['order']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='products', verbose_name="Kategoriya"
    )
    name = models.CharField(max_length=200, verbose_name="Nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    price = models.PositiveIntegerField(null=True, blank=True, verbose_name="Narxi (so'm)")
    box_price = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Qadoqdagi 1 dona narxi (so'm)",
        help_text="Qadoqlab sotilganda 1 donaning narxi (butun qadoq narxi emas). "
                   "Bo'sh qoldirilsa, mahsulot qadoqlab sotilmaydi."
    )
    image = models.ImageField(upload_to='products/', blank=True, verbose_name="Rasm")
    weight = models.CharField(max_length=50, blank=True, verbose_name="Og'irligi")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['order']

    def __str__(self):
        price = self.price if self.price is not None else 0
        return f"{self.name} — {price:,} so'm"