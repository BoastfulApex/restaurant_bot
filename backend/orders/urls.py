import os
import json
import requests
from django.conf import settings
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem


def notify_admin(order):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.ADMIN_CHAT_ID
    if not token or not chat_id:
        print("Telegram: token yoki chat_id yo'q")
        return

    base_url = f"https://api.telegram.org/bot{token}"
    items = list(order.items.select_related('product').all())
    items_text = "\n".join(
        f"  • {i.product_name} x{i.quantity} = {i.subtotal:,} so'm"
        for i in items
    )
    text = (
        f"🆕 <b>Yangi buyurtma #{order.id}</b>\n\n"
        f"👤 {order.full_name}\n"
        f"📞 {order.phone}\n"
        f"📍 {order.address or '—'}\n\n"
        f"🛒 Buyurtma:\n{items_text}\n\n"
        f"💰 Jami: <b>{order.total_price:,} so'm</b>\n"
        f"📝 Izoh: {order.note or '—'}"
    )

    try:
        # Matn xabar yuborish
        r = requests.post(f"{base_url}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }, timeout=10)
        print(f"Telegram sendMessage: {r.status_code} — {r.text}")

        # Mahsulot rasmlari (alohida)
        for item in items:
            if item.product and item.product.image:
                img_path = item.product.image.path
                if os.path.exists(img_path):
                    with open(img_path, 'rb') as f:
                        r2 = requests.post(f"{base_url}/sendPhoto", data={
                            "chat_id": chat_id,
                            "caption": item.product_name,
                        }, files={"photo": f}, timeout=10)
                        print(f"Telegram sendPhoto: {r2.status_code}")

        # Lokatsiya
        if order.latitude and order.longitude:
            r3 = requests.post(f"{base_url}/sendLocation", json={
                "chat_id": chat_id,
                "latitude": float(order.latitude),
                "longitude": float(order.longitude),
            }, timeout=10)
            print(f"Telegram sendLocation: {r3.status_code} — {r3.text}")

    except Exception as e:
        print(f"Telegram notify error: {e}")


@api_view(['POST'])
def create_order(request):
    data = request.data
    try:
        order = Order.objects.create(
            telegram_id=data.get('telegram_id', 0),
            full_name=data.get('full_name', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            total_price=data.get('total_price', 0),
            note=data.get('note', ''),
        )
        for item in data.get('items', []):
            OrderItem.objects.create(
                order=order,
                product_id=item.get('product_id'),
                product_name=item.get('name'),
                price=item.get('price'),
                quantity=item.get('quantity', 1),
            )
        notify_admin(order)
        return Response({'success': True, 'order_id': order.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"create_order error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


urlpatterns = [
    path('orders/', create_order, name='create_order'),
]
