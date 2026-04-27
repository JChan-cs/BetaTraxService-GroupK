from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_public_tenant(sender, **kwargs):
    # Only run for our specific app
    if sender.name == 'customers':
        # IMPORT MODELS HERE, inside the function
        from customers.models import Client, Domain
        import datetime

        # Now you can safely use them
        tenant, created = Client.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'Public Tenant',
                'paid_until': datetime.date(2099, 12, 31),
                'on_trial': False
            }
        )

        if created or not Domain.objects.filter(tenant=tenant).exists():
            # Domain.domain is globally unique, so look up by domain only.
            # Then ensure it points to the public tenant.
            domain_obj, _ = Domain.objects.get_or_create(
                domain='localhost',
                defaults={
                    'tenant': tenant,
                    'is_primary': True,
                },
            )
            if domain_obj.tenant_id != tenant.id or not domain_obj.is_primary:
                domain_obj.tenant = tenant
                domain_obj.is_primary = True
                domain_obj.save(update_fields=['tenant', 'is_primary'])

class CustomersConfig(AppConfig):
    name = 'customers'

    def ready(self):
        post_migrate.connect(create_public_tenant, sender=self)