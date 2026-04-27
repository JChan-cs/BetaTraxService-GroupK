from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    STATUS_CHOICES = [
        ('In progress', 'In progress'),
        ('Complete', 'Complete'),
    ]
    product_id = models.CharField(max_length=50, unique=True)
    version = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    product_owner = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_product'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In progress')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.product_id})"

class DeveloperAssignment(models.Model):
    # This OneToOneField ensures one developer -> one product
    developer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='developer_assignment',
    )
    # This ForeignKey ensures one product -> multiple developers
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='developer_assignments',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
