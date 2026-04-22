from django.db import models
from django.conf import settings

class DefectReport(models.Model):
    StatusC = [
        ("New", "New"),
        ("Open", "Open"),
        ("Rejected", "Rejected"),
        ("Duplicate", "Duplicate"),
        ("Assigned", "Assigned"),
        ("Cannot reproduce", "Cannot reproduce"),
        ("Fixed", "Fixed"),
        ("Resolved", "Resolved"),
        ("Reopened", "Reopened"),
    ]
    SeverityC = [
        ("Critical", "Critical"),
        ("Major", "Major"),
        ("Minor", "Minor"),
        ("Low", "Low"),
    ]
    PriorityC = [
        ("Critical", "Critical"),
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]
    ProductID = models.CharField(max_length=30)
    Version = models.CharField(max_length=30)
    ReportTitle = models.CharField(max_length=30)
    Description = models.CharField(max_length=200)
    Steps = models.TextField()
    TesterID = models.CharField(max_length=30)
    Email = models.EmailField(blank=True, null=True)
    Status = models.CharField(max_length=20, choices=StatusC, default="New")
    Severity = models.CharField(max_length=20, choices=SeverityC, blank=True, null=True)
    Priority = models.CharField(max_length=20, choices=PriorityC, blank=True, null=True)
    CreatedTime = models.DateTimeField(auto_now_add=True)
    UpdatedTime = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_defects',
    )
    

    def __str__(self):
        return f"{self.ReportTitle} - {self.Status}"

class DeveloperMetrics(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='developer_metrics'
    )
    defects_fixed = models.PositiveIntegerField(default=0)
    defects_reopened = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - Fixed: {self.defects_fixed}, Reopened: {self.defects_reopened}"