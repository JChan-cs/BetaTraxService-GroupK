from django.db import models

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
    """Through model linking a developer (User) to a Product.

    The DeveloperAssignment uses a OneToOneField on the developer to ensure
    a developer user can be assigned to at most one Product at a time.
    Multiple DeveloperAssignment rows may reference the same Product, so a
    product can have multiple developers.
    """
    developer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='developer_assignment',
        help_text='User assigned as a developer to exactly one product',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='developer_assignments',
        help_text='Product this developer is assigned to',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.developer.username} -> {self.product.product_id}"
