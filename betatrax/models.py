from django.db import models
from sympy import solve_univariate_inequality

# Create your models here.
class ProductOwner(models.Model):
    name = models.CharField(max_length=200)

class Developer(models.Model):
    name = models.CharField(max_length=200)
    assigned_id = models.CharField(max_length=200)

class BetaTester(models.Model):
    name = models.CharField(max_length=200)
    tester_id = models.CharField(max_length=200)
    email = models.CharField(max_length=200)

class DefectReport(models.Model):
    name = models.CharField(max_length=200)
    defect_id =  models.CharField(max_length=200)
    time = models.DateTimeField()
    status = models.CharField(max_length=20)
    severity = models.CharField(max_length=20)
    priority = models.CharField(max_length=20)