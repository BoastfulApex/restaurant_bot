from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BotUser


@api_view(['POST'])
def register_user(request):
    data = request.data
    telegram_id = data.get('telegram_id')
    if not telegram_id:
        return Response({'error': 'telegram_id is required'}, status=400)

    defaults = {
        'full_name': data.get('full_name', ''),
        'username': data.get('username', ''),
    }
    if data.get('phone'):
        defaults['phone'] = data.get('phone')

    user, _ = BotUser.objects.update_or_create(telegram_id=telegram_id, defaults=defaults)
    return Response({'success': True, 'id': user.id})


urlpatterns = [
    path('users/register/', register_user, name='register_user'),
]
