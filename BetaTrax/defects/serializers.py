from rest_framework import serializers
from .models import DefectReport
from comments.models import Comment

class DefectReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        fields = "__all__"
        read_only_fields = ["Status", "CreatedTime", "UpdatedTime", "assigned_to"]
        extra_kwargs = {
            "Severity": {"required": False},
            "Priority": {"required": False},
            "assigned_to": {"required": False},
        }


class DefectReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        fields = ["id", "Status"]
        read_only_fields = ["id"]

    def validate_Status(self, value):
        instance = self.instance
        if instance is None:
            raise serializers.ValidationError("Instance not found.")

        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError("Request context is required.")

        current_status = instance.Status
        target_status = value
        transition = (current_status, target_status)

        group_names = set(request.user.groups.values_list("name", flat=True))

        is_beta_tester = "BetaTester" in group_names
        is_developer = "Developer" in group_names
        is_product_owner = "ProductOwner" in group_names

        transitions = {
            ("Assigned", "Fixed"): {"role": is_developer, "name": "Developer"},
            ("Fixed", "Resolved"): {"role": is_product_owner, "name": "ProductOwner"},
        }

        rule = transitions.get(transition)
        if rule is None:
            raise serializers.ValidationError(
                f"Invalid status transition from '{current_status}' to '{target_status}'."
            )

        if not rule["role"]:
            raise serializers.ValidationError(
                f"Only usergroup {rule['name']} can change status from '{current_status}' to '{target_status}'."
            )
        
        if transition == ("Assigned", "Fixed") and instance.assigned_to != request.user:
            raise serializers.ValidationError(
                "Only the assigned developer can mark this report as Fixed."
            )
        return value

class DefectEvaluationSerializer(serializers.ModelSerializer):
    # These fields aren't on the model but are needed for the triage process
    action = serializers.ChoiceField(choices=['accept', 'reject', 'duplicate'], required=False)
    duplicate_id = serializers.IntegerField(required=False, allow_null=True)
    comment_text = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = DefectReport
        fields = ['Severity', 'Priority', 'action', 'duplicate_id', 'comment_text']
        extra_kwargs = {
            'Severity': {'required': False},
            'Priority': {'required': False},
        }

    def validate(self, data):
        # Business Logic: If action is 'duplicate', duplicate_id is mandatory
        if data.get('action') == 'duplicate' and not data.get('duplicate_id'):
            raise serializers.ValidationError({"duplicate_id": "Original report ID is required for duplicates."})
        
        if data.get('duplicate_id'):
            if not DefectReport.objects.filter(pk=data['duplicate_id']).exists():
                raise serializers.ValidationError({"duplicate_id": "The original report ID does not exist."})
        return data

    def update(self, instance, validated_data):
        # 1. Update standard fields (Severity/Priority)
        instance.Severity = validated_data.get('Severity', instance.Severity)
        instance.Priority = validated_data.get('Priority', instance.Priority)

        # 2. Update Status based on action
        action = validated_data.get('action')
        if action == 'accept':
            instance.Status = 'Open'
        elif action == 'reject':
            instance.Status = 'Rejected'
        elif action == 'duplicate':
            instance.Status = 'Duplicate'
        
        instance.save()

        # 3. Handle Comment Creation (if user is authenticated)
        comment_text = validated_data.get('comment_text')
        user = self.context.get('request').user
        if comment_text and user and user.is_authenticated:
            Comment.objects.create(author=user, text=comment_text)

        return instance