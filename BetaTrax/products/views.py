from rest_framework import viewsets, permissions
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product
from .serializers import ProductSerializer

# API viewset for REST endpoints
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='ProductOwner').exists():
            return Product.objects.filter(product_owner=user)
        return Product.objects.none()

    def perform_create(self, serializer):
        serializer.save(product_owner=self.request.user)

# HTML dashboard view
@login_required
def product_dashboard(request):
    products = Product.objects.filter(product_owner=request.user)
    return render(request, 'products/dashboard.html', {'products': products})
