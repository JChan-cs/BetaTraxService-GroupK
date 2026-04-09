from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, product_dashboard

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', product_dashboard, name='product_dashboard'),
]