from django.db import models
from django.contrib.auth.models import User

class Result(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    report_id = models.CharField(max_length=100) # Matches view filter
    retest_result = models.TextField()
    date = models.DateField(auto_now_add=True) # Matches view filter

    def __str__(self):
        return f"Report {self.report_id}"
    

