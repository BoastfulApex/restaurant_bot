from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer


@api_view(['GET'])
def menu(request):
    categories = Category.objects.filter(is_active=True).prefetch_related('products')
    # Faqat faol mahsulotlar
    data = []
    for cat in categories:
        active_products = cat.products.filter(is_active=True)
        if active_products.exists():
            s = CategorySerializer(cat, context={'request': request})
            cat_data = s.data
            cat_data['products'] = [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'price': p.price,
                    'image': request.build_absolute_uri(p.image.url) if p.image else None,
                    'weight': p.weight,
                }
                for p in active_products
            ]
            data.append(cat_data)
    return Response(data)


urlpatterns = [
    path('menu/', menu, name='menu'),
]
