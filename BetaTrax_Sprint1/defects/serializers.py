from rest_framework import serializers
from .models import DefectReport

class DefectReportSerializer(serializers.ModelSerializer):
  class Meta:
    model = DefectReport
    fields = "__all__"
    read_only_fields = ["Status", "CreatedTime", "UpdatedTime"]
    extra_kwargs = {"Severity":{"required": False}, "Priority":{"required": False}}

class DefectReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        fields = ['id', 'Status']
        read_only_fields = ['id']
    
    def validate_Status(self, value):
        instance = self.instance
        if instance is None:
            raise serializers.ValidationError("Instance not found.")
        current_status = instance.Status
        
        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError("Request context is required.")
        user = request.user

        group_names = set(user.groups.values_list('name', flat=True))
        
        is_beta_tester = 'BetaTester' in group_names
        is_developer = 'Developer' in group_names
        _is_product_owner = 'ProductOwner' in group_names
        
        if is_beta_tester:
            if current_status != 'Fixed' or value != 'Resolved':
                raise serializers.ValidationError("Beta Testers can only change status from 'Fixed' to 'Resolved'.")

        if is_developer:
            if current_status != 'Assigned' or value != 'Fixed':
                raise serializers.ValidationError("Developers can only change status from 'Assigned' to 'Fixed'.")
        return value
