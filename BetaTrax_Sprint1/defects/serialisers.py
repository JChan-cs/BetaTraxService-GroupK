from rest_framework import serializers
from .models import DefectReport

class DefectReportSerializer(serializers.ModelSerializer):
  class Meta:
    model = DefectReport
    fields = "__all__"
    read_only_fields = ["Status", "CreatedTime", "UpdatedTime"]
    extra_kwargs = {"Severity":{"required": False}, "Priority":{"required": False}}
