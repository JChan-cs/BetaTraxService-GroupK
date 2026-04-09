from django.contrib import admin

from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'version', 'product_owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product_id', 'name', 'product_owner__username')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('product_id', 'version', 'name', 'product_owner', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
