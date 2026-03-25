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
  ("Major", "Major"),
  ("Minor", "Minor"),
  ("Low", "Low")]
  ProductID = models.CharField(max_length = 30)
  Version = models.CharField(max_length = 30)
  ReportTitle = models.CharField(max_length = 30)
  Description = models.TextField()
  Steps = models.TextField()
  TesterID = models.CharField(max_length = 30)
  Email = models.EmailField(blank = True, null = True)
  Status = models.CharField(max_length = 20, choice = StatusC, default = "New")
  Severity = models.CharField(max_length = 20, choice = SeverityC)
  Priority = models.CharField(max_length = 20, choice = PriorityC)
  AssignedPerson = models.CharField(max_length = 30)
  CreatedTime = models.DataTimeField(auto_now_added = True)
  UpdatedTime = models.DataTimeField(auto_now = True)

def __str__(self):
        return f"{self.ReportTitle} - {self.status}"
  
