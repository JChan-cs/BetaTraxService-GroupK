from django.db import models
from django.conf import settings
from django.utils import timezone

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
    ProductID = models.CharField(max_length=30, help_text="Unique identifier for the product associated.")
    Version = models.CharField(max_length=30, help_text="The version of the product the report is applicable to.")
    ReportTitle = models.CharField(max_length=30, help_text="A brief title for the defect report.")
    Description = models.CharField(max_length=200, help_text="A detailed description of the defect.")
    Steps = models.TextField(help_text="The steps to reproduce the defect.")
    TesterID = models.CharField(max_length=30, help_text="The ID of the tester who submitted the report.")
    Email = models.EmailField(blank=True, null=True, help_text="Contact email for the tester, optional.")
    Status = models.CharField(max_length=20, choices=StatusC, default="New", help_text="Current status of the defect report.")
    Severity = models.CharField(max_length=20, choices=SeverityC, blank=True, null=True, help_text="The severity level of the defect.")
    Priority = models.CharField(max_length=20, choices=PriorityC, blank=True, null=True, help_text="The priority level of the defect.")
    CreatedTime = models.DateTimeField(
        default=timezone.now, 
        help_text="The timestamp when the report was created. Can be edited manually."
    )
    UpdatedTime = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_defects',
        help_text="The user to whom this defect is currently assigned. Can be null if unassigned."
    )
    duplicate_of = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duplicates',
        help_text='Original report if this report is marked as duplicate.',
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
    
class Comment(models.Model):
    defect = models.ForeignKey(
        DefectReport, 
        on_delete=models.CASCADE, 
        related_name='defect_comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='defect_comment_authors'
    )
    text = models.TextField()
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="The time this comment was posted."
    )

    def __str__(self):
        return f"Comment by {self.author.username} on {self.defect.id}"