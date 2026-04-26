from rest_framework import serializers
from django.core.mail import send_mail
from .models import DefectReport
from comments.models import Comment

class DefectReportSerializer(serializers.ModelSerializer):
    """Defect report submitted by a user, containing details about the issue and its lifecycle status."""
    class Meta:
        model = DefectReport
        fields = "__all__"
        read_only_fields = ["Status", "CreatedTime", "UpdatedTime", "assigned_to", "duplicate_of"]
        extra_kwargs = {
            "Severity": {"required": False},
            "Priority": {"required": False},
            "assigned_to": {"required": False},
        }


class DefectReportStatusSerializer(serializers.ModelSerializer):
    """Partial defect report focused on status updates, with validation to enforce lifecycle rules."""
    class Meta:
        model = DefectReport
        fields = ["id", "Status", "assigned_to"]
        read_only_fields = ["id"]

    def validate(self, new_instance):
        old_instance = self.instance
        if old_instance is None:
            raise serializers.ValidationError("Instance not found.")

        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError("Request context is required.")

        old_status = old_instance.Status
        new_status = new_instance.get("Status")
        transition = (old_status, new_status)

        group_names = set(request.user.groups.values_list("name", flat=True))

        is_developer = "Developer" in group_names
        is_product_owner = "ProductOwner" in group_names

        transitions = {
            ("Assigned", "Fixed"): {"role": is_developer, "name": "Developer"},
            ("Assigned", "Cannot reproduce"): {"role": is_developer, "name": "Developer"},
            ("Fixed", "Resolved"): {"role": is_product_owner, "name": "ProductOwner"},
            ("Fixed", "Reopened"): {"role": is_product_owner, "name": "ProductOwner"},
            ("Reopened", "Assigned"): {"role": is_developer, "name": "Developer"},
        }

        rule = transitions.get(transition)
        if rule is None:
            raise serializers.ValidationError(
                f"Invalid status transition from '{old_status}' to '{new_status}'."
            )

        if not rule["role"]:
            raise serializers.ValidationError(
                f"Only usergroup {rule['name']} can change status from '{old_status}' to '{new_status}'."
            )

        if transition in {("Assigned", "Fixed"), ("Assigned", "Cannot reproduce")} and old_instance.assigned_to != request.user:
            raise serializers.ValidationError(
                "Only the assigned developer can update this Assigned report."
            )
        if transition in {("Fixed", "Reopened"), ("Assigned", "Cannot reproduce")}:
            # Unassign reopened reports to allow reassignment
            # assign None (PK expected by related field)
            new_instance["assigned_to"] = None
        if transition == ("Reopened", "Assigned"):
            # Reassign to the user performing the action
            # serializers expect a PK value for relational fields when passed in data,
            # so convert the user instance into its PK here.
            new_instance["assigned_to"] = request.user.pk if hasattr(request.user, 'pk') else request.user
        return new_instance

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
            if self.instance and data['duplicate_id'] == self.instance.pk:
                raise serializers.ValidationError({"duplicate_id": "A report cannot be a duplicate of itself."})
        return data

    def update(self, instance, validated_data):
        # 1. Update standard fields (Severity/Priority)
        instance.Severity = validated_data.get('Severity', instance.Severity)
        instance.Priority = validated_data.get('Priority', instance.Priority)
        system_message = None
        duplicate_target = None

        # 2. Update Status based on action
        action = validated_data.get('action')
        if action == 'accept':
            instance.Status = 'Open'
            system_message = f"System: Report #{instance.id} accepted. Status set to 'Open' (Severity: {instance.Severity}, Priority: {instance.Priority})."
        elif action == 'reject':
            instance.Status = 'Rejected'
            system_message = f"System: Report #{instance.id} has been rejected."
        elif action == 'duplicate':
            duplicate_target = DefectReport.objects.get(pk=validated_data.get('duplicate_id'))
            instance.Status = 'Duplicate'
            instance.duplicate_of = duplicate_target
            system_message = f"System: Report #{instance.id} marked as duplicate of Report #{duplicate_target.id}."
        
        instance.save()

        # 3. Handle Comment Creation (if user is authenticated)        
        user = self.context.get('request').user
        if user and user.is_authenticated:
            # Create automated status update comment
            if system_message:
                Comment.objects.create(author=user, defect=instance, text=system_message)

            if action == 'duplicate' and duplicate_target is not None:
                Comment.objects.create(
                    author=user,
                    defect=duplicate_target,
                    text=f"System: Report #{instance.id} was marked as a duplicate of this report.",
                )

                recipients = {email for email in [instance.Email, duplicate_target.Email] if email}
                if recipients:
                    send_mail(
                        subject=f"BetaTrax: Duplicate report linked (#{instance.id} -> #{duplicate_target.id})",
                        message=(
                            "Hello,\n\n"
                            f"Report #{instance.id} has been marked as a duplicate of report #{duplicate_target.id}.\n"
                            f"Current status for report #{instance.id}: {instance.Status}\n"
                            "You are receiving this because your email is attached to one of the linked reports."
                        ),
                        from_email='noreply@betatrax.com',
                        recipient_list=list(recipients),
                        fail_silently=True,
                    )
            
            # Create manual comment text if provided by the PO
            comment_text = validated_data.get('comment_text')
            if comment_text:
                Comment.objects.create(author=user, defect=instance, text=comment_text)

        return instance