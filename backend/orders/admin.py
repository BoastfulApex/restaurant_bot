from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


STATUS_COLORS = {
    'new': '#3498db',
    'confirmed': '#27ae60',
    'cooking': '#e67e22',
    'delivering': '#9b59b6',
    'done': '#2ecc71',
    'cancelled': '#e74c3c',
}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'quantity', 'subtotal_display']
    fields = ['product_name', 'price', 'quantity', 'subtotal_display']
    can_delete = False

    def subtotal_display(self, obj):
        return format_html('<b>{:,} so\'m</b>', obj.subtotal)
    subtotal_display.short_description = "Jami"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'full_name', 'phone', 'total_price_display', 'status_badge', 'status', 'created_at']
    list_editable = ['status']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'phone']
    list_per_page = 25
    readonly_fields = ['telegram_id', 'full_name', 'phone', 'address', 'map_link', 'total_price', 'created_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Mijoz', {'fields': ('telegram_id', 'full_name', 'phone')}),
        ('Manzil', {'fields': ('address', 'map_link')}),
        ('Buyurtma', {'fields': ('total_price', 'note', 'status')}),
        ('Vaqt', {'fields': ('created_at',)}),
    )

    def order_id(self, obj):
        return format_html('<b>#{}</b>', obj.id)
    order_id.short_description = "ID"
    order_id.admin_order_field = 'id'

    def total_price_display(self, obj):
        return format_html('<b style="color:#f39c12">{} so\'m</b>', f"{obj.total_price:,}")
    total_price_display.short_description = "Jami"
    total_price_display.admin_order_field = 'total_price'

    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, '#999')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:bold">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def map_link(self, obj):
        if obj.latitude and obj.longitude:
            url = f"https://maps.google.com/?q={obj.latitude},{obj.longitude}"
            return format_html('<a href="{}" target="_blank">📍 Xaritada ko\'rish</a>', url)
        return '—'
    map_link.short_description = "Lokatsiya"
