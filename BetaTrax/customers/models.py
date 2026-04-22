from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField()
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True

class Domain(DomainMixin):
    # Manually defining this makes the relationship "stronger" 
    # and prevents the 'ForeignKey([])' error.
    tenant = models.ForeignKey(
        Client, 
        db_index=True, 
        related_name='domains', 
        on_delete=models.CASCADE
    )