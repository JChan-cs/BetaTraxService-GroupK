from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from customers.models import Client, Domain

class DomainInline(admin.TabularInline):
    model = Domain
    max_num = 1
    extra = 1

@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'paid_until', 'schema_name')
    inlines = [DomainInline]

# You can also register Domain separately if you want to edit it later
@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')