from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_id', 'version', 'name', 'status', 'created_at']
        read_only_fields = ['created_at']