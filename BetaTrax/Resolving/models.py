from django.db import models
from django.contrib.auth.models import User

class Result(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, help_text="The user who submitted the retest result.")
    report_id = models.CharField(max_length=100, help_text="The ID of the defect report.")
    retest_result = models.TextField(help_text="The result of the retest.")
    date = models.DateTimeField(auto_now_add=True, help_text="The date and time when the retest result was submitted.")

    def __str__(self):
        return f"Report {self.report_id}"
    

