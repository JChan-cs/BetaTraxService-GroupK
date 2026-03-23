from django.db import models

# Create your models here.
class ProductOwner(models.Model):
    name = models.CharField(max_length=200)

class Developer(models.Model):
    name = models.CharField(max_length=200)
    assigned_id = models.CharField(max_length=200)

class BetaTester(models.Model):
    name = models.CharField(max_length=200)

class DefectReport(models.Model):
    name = models.CharField(max_length=200)
    id =  models.CharField(max_length=200)
    time = models.DateTimeField()
    status = models.CharField(max_length=10)