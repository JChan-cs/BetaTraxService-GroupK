from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(ProductOwner)
admin.site.register(Developer)
admin.site.register(DefectReport)