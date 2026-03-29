from rest_framework import serializers

from defects.models import DefectReport

class DefectReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        fields = ['id', 'status']
        read_only_fields = ['id']
    
    def validate_status(self, value):
        instance = self.instance
        if instance is None:
            raise serializers.ValidationError("Instance not found.")
        current_status = instance.status
        
        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError("Request context is required.")
        user = request.user

        group_names = set(user.groups.values_list('name', flat=True))
        
        is_beta_tester = 'BetaTester' in group_names
        is_developer = 'Developer' in group_names
        _is_product_owner = 'ProductOwner' in group_names
        
        if is_beta_tester:
            if current_status != 'FIXED' or value != 'RESOLVED':
                raise serializers.ValidationError("Beta Testers can only change status from 'FIXED' to 'RESOLVED'.")

        if is_developer:
            if current_status != 'ASSIGNED' or value != 'FIXED':
                raise serializers.ValidationError("Developers can only change status from 'ASSIGNED' to 'FIXED'.")
        return value

class DefectReportSerializer(serializers.Serializer):
    report_id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    status = serializers.CharField(max_length=20, read_only=True)