import os
import json
import requests
from django.conf import settings
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from users.models import BotUser


def format_phone(phone):
    digits = ''.join(ch for ch in phone if ch.isdigit())
    if digits.startswith('998'):
        digits = digits[3:]
    return f"+998 {digits}"


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
    order_text = (
        f"🆕 <b>Yangi buyurtma #{order.id}</b>\n\n"
        f"👤 {order.full_name}\n"
        f"📞 {format_phone(order.phone)}\n"
        f"📍 {order.address or '—'}\n\n"
        f"🛒 Buyurtma:\n{items_text}\n\n"
        f"💰 Jami: <b>{order.total_price:,} so'm</b>\n"
        f"📝 Izoh: {order.note or '—'}"
    )

    try:
        # Rasmli mahsulotlarni yig'ish
        photos = []
        for item in items:
            if item.product and item.product.image:
                img_path = item.product.image.path
                if os.path.exists(img_path):
                    photos.append((img_path, item.product_name))

        # Media group yuborish (max 10 ta har bir guruhda)
        BATCH = 10
        batches = [photos[i:i+BATCH] for i in range(0, len(photos), BATCH)] if photos else []

        for batch_idx, batch in enumerate(batches):
            is_last = (batch_idx == len(batches) - 1)
            media = []
            files = {}
            for idx, (img_path, name) in enumerate(batch):
                key = f"photo{idx}"
                media.append({
                    "type": "photo",
                    "media": f"attach://{key}",
                    # Oxirgi guruhning oxirgi rasmiga caption qo'shilmaydi — alohida text yuboriladi
                })
                files[key] = open(img_path, 'rb')

            try:
                r = requests.post(f"{base_url}/sendMediaGroup", data={
                    "chat_id": chat_id,
                    "media": json.dumps(media),
                }, files=files, timeout=30)
                print(f"Telegram sendMediaGroup batch {batch_idx}: {r.status_code}")
            finally:
                for f in files.values():
                    f.close()

        # Order detallari matni — oxirgi mediagroupdan keyin (yoki rasm yo'q bo'lsa ham)
        r2 = requests.post(f"{base_url}/sendMessage", json={
            "chat_id": chat_id,
            "text": order_text,
            "parse_mode": "HTML",
        }, timeout=10)
        print(f"Telegram sendMessage: {r2.status_code}")

        # Lokatsiya
        if order.latitude and order.longitude:
            r3 = requests.post(f"{base_url}/sendLocation", json={
                "chat_id": chat_id,
                "latitude": float(order.latitude),
                "longitude": float(order.longitude),
            }, timeout=10)
            print(f"Telegram sendLocation: {r3.status_code}")

    except Exception as e:
        print(f"Telegram notify error: {e}")


def sync_bot_user(telegram_id, full_name='', username='', phone=''):
    if not telegram_id:
        return
    defaults = {}
    if full_name:
        defaults['full_name'] = full_name
    if username:
        defaults['username'] = username
    if phone:
        defaults['phone'] = phone
    BotUser.objects.update_or_create(telegram_id=telegram_id, defaults=defaults)


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
        sync_bot_user(
            order.telegram_id,
            full_name=order.full_name,
            username=data.get('username', ''),
            phone=order.phone,
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
