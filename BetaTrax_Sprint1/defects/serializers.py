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
    # Check if the DefectReport instance exists
    instance = self.instance
    if instance is None:
      raise serializers.ValidationError("Instance not found.")
    
    # Get the request from the context
    request = self.context.get("request")
    if request is None:
      raise serializers.ValidationError("Request context is required.")

    current_status = instance.Status
    target_status = value
    transition = (current_status, target_status)
    
    group_names = set(request.user.groups.values_list('name', flat=True))
    
    is_beta_tester = 'BetaTester' in group_names
    is_developer = 'Developer' in group_names
    _is_product_owner = 'ProductOwner' in group_names # Reserved for future use
    
    # Allowed status changes and their required roles
    transitions = {
      ('Assigned', 'Fixed'): {"role": is_developer, "name": "Developer"},
      ('Fixed', 'Resolved'): {"role": is_beta_tester, "name": "BetaTester"},
    }
    
    rule = transitions.get(transition)
    if rule is None:
      raise serializers.ValidationError(f"Invalid status transition from '{current_status}' to '{target_status}'.")
    
    if not rule["role"]:
      raise serializers.ValidationError(f"Only usergroup {rule['name']} can change status from '{current_status}' to '{target_status}'.")
    return value
