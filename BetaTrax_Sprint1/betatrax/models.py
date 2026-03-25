from django.db import models

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone

# Create your models here.
class ProductOwner(models.Model):
    name = models.CharField(max_length=200)

class Developer(models.Model):
    name = models.CharField(max_length=200)

class BetaTester(models.Model):
    name = models.CharField(max_length=200)
    tester_id = models.CharField(max_length=20)
    email = models.CharField(max_length=200)

class DefectReport(models.Model):
    STATUS_CHOICES = [
        ("NEW", "New"),
        ("OPENED", "Opened"),
        ("REJECTED", "Rejected"),
        ("ASSIGNED", "Assigned"),
        ("RESOLVED", "Resolved"),
    ]

    SEVERITY = [

    ]

    PRIORITY = [

    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, status=STATUS_CHOICES, default="NEW")

    # Relations
    created_by = models.ForeignKey(
        ProductOwner, related_name="reports_created", on_delete=models.CASCADE
    )
    assigned_to = models.ForeignKey(
        Developer, related_name="reports_assigned", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.title} ({self.status})"

    # --- Product Owner actions ---
    def accept(self, user):
        if user.groups.filter(name="ProductOwner").exists():
            self.status = "OPENED"
            self.save()

    def reject(self, user):
        if user.groups.filter(name="ProductOwner").exists():
            self.status = "REJECTED"
            self.save()

    # --- Developer actions ---
    def assign_to_self(self, user):
        if user.groups.filter(name="Developer").exists():
            self.assigned_to = user
            self.status = "ASSIGNED"
            self.save()

# --- Utility function to create groups if not exist ---
def create_default_groups():
    groups = ["ProductOwner", "Developer", "BetaTester"]
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)

class Assign(models.Model):
    time = models.DateTimeField()
    status = models.CharField(max_length=10)
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    reports = models.ManyToManyField(DefectReport, through='Assignreport')




