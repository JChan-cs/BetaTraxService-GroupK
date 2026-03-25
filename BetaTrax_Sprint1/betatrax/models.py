from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Create your models here.
class ProductOwner(models.Model):
    username = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"ProductOwner: {self.user.username}"

class Developer(models.Model):
    username = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"ProductOwner: {self.user.username}"

class BetaTester(models.Model):
    username = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tester_id = models.CharField(max_length=20)
    email = models.CharField(max_length=200)

    def __str__(self):
        return f"ProductOwner: {self.user.username}"
    

class DefectReport(models.Model):
    STATUS_CHOICES = [
        ("NEW", "New"),
        ("OPENED", "Opened"),
        ("REJECTED", "Rejected"),
        ("ASSIGNED", "Assigned"),
        ("FIXED", "Fixed"),
        ("RESOLVED", "Resolved"),
        ("REOPENED", "Reopened"),
    ]

    SEVERITY_CHOICES = [
        ("CRITICAL", "Critical"),
        ("MAJOR", "Major"),
        ("MINOR", "Minor"),
        ("LOW", "Low"),
    ]

    PRIORITY_CHOICES = [
        ("CRITICAL", "Critical"),
        ("HIGH", "High"),
        ("MEDIUM", "Medium"),
        ("LOW", "Low"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW")
    report_id = models.CharField(max_length=36, unique=True, editable=False, default=uuid.uuid4)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="MINOR")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM")

    # Relations
    created_by = models.ForeignKey(
        BetaTester, related_name="reports_created", on_delete=models.CASCADE
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
            try:
                dev = Developer.objects.get(user=user)
            except Developer.DoesNotExist:
                return False
            self.assigned_to = dev
            self.status = self.STATUS_ASSIGNED
            self.save()
            return True





