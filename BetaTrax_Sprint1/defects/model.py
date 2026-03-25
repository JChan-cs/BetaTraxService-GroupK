from django.db import models
class DefectsReport(models.Model):
  StatusC = [
    ("New","New"),
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
  ("Low", "Low")]
  PriorityC = [
  ("Critical", "Critical"),
  ("High", "High"),
  ("Medium", "Medium"),
  ("Low", "Low")]
  ProductID = models.CharField(max_length = 30)
  Version = models.CharField(max_length = 30)
  ReportTitle = models.CharField(max_length = 30)
  Description = models.TextField()
  Steps = models.TextField()
  TesterID = models.CharField(max_length = 30)
  Email = models.EmailField(blank = True, null = True)
  Status = models.CharField(max_length = 20, choices = StatusC, default = "New")
  Severity = models.CharField(max_length = 20, choices = SeverityC)
  Priority = models.CharField(max_length = 20, choices = PriorityC)
  AssignedPerson = models.CharField(max_length = 30)
  CreatedTime = models.DateTimeField(auto_now_add = True)
  UpdatedTime = models.DateTimeField(auto_now = True)

def __str__(self):
        return f"{self.ReportTitle} - {self.Status}"
  
