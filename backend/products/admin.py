from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'product_count', 'is_active']
    list_editable = ['order', 'is_active']
    ordering = ['order']

    def product_count(self, obj):
        count = obj.products.filter(is_active=True).count()
        return format_html('<b>{}</b> ta', count)
    product_count.short_description = "Mahsulotlar"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'category', 'price_display', 'weight', 'is_active']
    list_editable = ['is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    list_per_page = 20
    readonly_fields = ['image_preview_large', 'created_at']
    fieldsets = (
        ('Asosiy', {'fields': ('category', 'name', 'description', 'weight')}),
        ('Narx va holat', {'fields': ('price', 'is_active')}),
        ('Rasm', {'fields': ('image', 'image_preview_large')}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:8px;"/>',
                obj.image.url
            )
        return '—'
    image_preview.short_description = "Rasm"

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:200px;object-fit:cover;border-radius:12px;"/>',
                obj.image.url
            )
        return '—'
    image_preview_large.short_description = "Rasm ko'rinishi"

    def price_display(self, obj):
        return format_html('<b style="color:#f39c12">{} so\'m</b>', f"{obj.price:,}")
    price_display.short_description = "Narxi"
    price_display.admin_order_field = 'price'
