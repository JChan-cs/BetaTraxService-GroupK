from django.contrib import admin
from .models import Product, DeveloperAssignment

# Create an inline to manage assignments
class DeveloperAssignmentInline(admin.TabularInline):
    model = DeveloperAssignment
    extra = 1
    autocomplete_fields = ['developer']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Removed 'developers' from list_display
    list_display = ('product_id', 'name', 'version', 'product_owner', 'status', 'created_at', 'get_developers')
    list_filter = ('status', 'created_at')
    search_fields = ('product_id', 'name', 'product_owner__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            # Removed 'developers' from fields list here
            'fields': ('product_id', 'version', 'name', 'product_owner', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    inlines = [DeveloperAssignmentInline]

    # Optional: Helper method to show developers in the list view
    def get_developers(self, obj):
        return ", ".join([da.developer.username for da in obj.developer_assignments.all()])
    get_developers.short_description = 'Developers'