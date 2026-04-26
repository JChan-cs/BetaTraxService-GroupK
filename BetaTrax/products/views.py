from rest_framework import viewsets, permissions
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
import json
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
        # When creating via API, the authenticated user becomes owner unless
        # a product_owner is explicitly provided and permitted by serializer.
        # If the request contains 'developers' as repeated params from the
        # HTML form (name='developer'), DRF will already make that available
        # in serializer.validated_data. We simply save here.
        serializer.save()

# HTML dashboard view
@login_required
def product_dashboard(request):
    User = get_user_model()
    products = Product.objects.filter(product_owner=request.user)
    owners = User.objects.filter(
        Q(is_superuser=True) | Q(groups__name='ProductOwner'),
        is_active=True,
    ).distinct()
    developer_options = User.objects.filter(is_active=True, groups__name='Developer').distinct()

    if request.method == 'POST':
        # Collect developers list from repeated 'developer' inputs
        selected_developers = request.POST.getlist('developer')

        form_data = {
            'product_id': request.POST.get('product_id'),
            'version': request.POST.get('version'),
            'name': request.POST.get('name'),
            'status': request.POST.get('status') or 'In progress',
            'product_owner': request.POST.get('product_owner'),
            'developers': selected_developers,
        }

        serializer = ProductSerializer(data=form_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            products = Product.objects.filter(product_owner=request.user)
            return render(
                request,
                'products/dashboard.html',
                {
                    'products': products,
                    'owners': owners,
                    'developers': developer_options,
                    'pre_selected_developers_json': '[]',
                    'success': True,
                },
            )
        else:
            return render(
                request,
                'products/dashboard.html',
                {
                    'products': products,
                    'owners': owners,
                    'developers': developer_options,
                    'errors': serializer.errors,
                    'form_data': form_data,
                    'pre_selected_developers_json': json.dumps(selected_developers),
                },
            )

    return render(
        request,
        'products/dashboard.html',
        {
            'products': products,
            'owners': owners,
            'developers': developer_options,
            'pre_selected_developers_json': '[]',
        },
    )
