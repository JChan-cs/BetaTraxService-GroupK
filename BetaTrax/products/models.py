from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    STATUS_CHOICES = [
        ('In progress', 'In progress'),
        ('Complete', 'Complete'),
    ]
    product_id = models.CharField(max_length=50, unique=True, help_text="Unique identifier for the product.")
    version = models.CharField(max_length=20, help_text="The current version of the product.")
    name = models.CharField(max_length=100, help_text="The name of the product.")

    product_owner = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_product',
        help_text="The user who owns this product.",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In progress', help_text="The release status of the product.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The timestamp when the product was created.")

    def __str__(self):
        return f"{self.name} ({self.product_id})"

class DeveloperAssignment(models.Model):
    # This OneToOneField ensures one developer -> one product
    developer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='developer_assignment',
        help_text='User assigned as a developer to exactly one product',
    )
    # This ForeignKey ensures one product -> multiple developers
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='developer_assignments',
        help_text='Product this developer is assigned to',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
