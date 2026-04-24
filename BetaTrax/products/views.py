from rest_framework import viewsets, permissions
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product
from .serializers import ProductSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

# API viewset for REST endpoints

@extend_schema(tags=['products'])
@extend_schema_view(
    list=extend_schema(
        summary="List products", 
        description="Retrieve products in the caller's visibility scope. Superusers and ProductOwner users receive products where product_owner is themselves; other authenticated users receive an empty list.",
        responses={
            200: OpenApiResponse(
                response=ProductSerializer(many=True),
                description="Products retrieved successfully"
            ),
            403: OpenApiResponse(description="Authentication required")
        }
    ),
    create=extend_schema(
        summary="Create product", 
        description="Create a new product owned by the authenticated user.",
        request=ProductSerializer,
        responses={
            201: OpenApiResponse(
                response=ProductSerializer,
                description="Product created successfully"
            ),
            400: OpenApiResponse(description="Invalid input data"),
            403: OpenApiResponse(description="Authentication required")
        }
    ),
    retrieve=extend_schema(
        summary="Get product", 
        description="Retrieve a single product by ID within your visibility scope.",
        responses={
            200: OpenApiResponse(response=ProductSerializer, description="Product retrieved successfully"),
            403: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Product not found")
        }
    ),
    update=extend_schema(
        summary="Update product", 
        description="Update an existing product within your visibility scope.",
        request=ProductSerializer,
        responses={
            200: OpenApiResponse(response=ProductSerializer, description="Product fully updated successfully"),
            400: OpenApiResponse(description="Invalid input data"),
            403: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Product not found")
        }

    ),
    partial_update=extend_schema(
        summary="Partially update product", 
        description="Partially update an existing product within your visibility scope.",
        request=ProductSerializer,
        responses={
            200: OpenApiResponse(response=ProductSerializer, description="Product partially updated successfully"),
            400: OpenApiResponse(description="Invalid input data"),
            403: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Product not found")
        }

    ),
    destroy=extend_schema(
        summary="Delete product",
        description="Delete an existing product within your visibility scope.",
        responses={
            204: OpenApiResponse(description="Product deleted successfully"),
            403: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Product not found")
        }
    )
)
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
