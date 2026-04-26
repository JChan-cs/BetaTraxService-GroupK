from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import DefectReport
from .developer_metrics import apply_status_transition_metrics
from Resolving.models import Result

def send_status_update_email(instance, is_created, is_duplicate_update=False):
    """
    Helper function to execute the actual email sending logic.
    If is_duplicate_update is True, the messaging explicitly mentions the duplication relationship.
    """
    if not instance.Email:
        return

    if is_created:
        subject = f"BetaTrax: New Report Submitted - {instance.ReportTitle}"
        message = (
            f"Hello,\n\n"
            f"Your report #{instance.id} has been received.\n"
            f"Status: {instance.Status}\n\n"
            f"A Product Owner will evaluate it shortly."
        )
    elif is_duplicate_update:
        subject = f"BetaTrax: Duplicate Report Update - #{instance.id}"
        message = (
            f"Hello,\n\n"
            f"Your report #{instance.id} is marked as a duplicate of report #{instance.duplicate_of_id}.\n"
            f"Please be informed that the status of your duplicated report has changed to '{instance.Status}' "
            f"following an update to the original report."
        )
    else:
        subject = f"BetaTrax: Update on Report #{instance.id}"
        message = (
            f"Hello,\n\n"
            f"Your report '{instance.ReportTitle}' has been updated.\n"
            f"New Status: {instance.Status}\n"
            f"Severity: {instance.Severity if instance.Severity else 'TBD'}\n"
            f"Priority: {instance.Priority if instance.Priority else 'TBD'}"
        )

    send_mail(
        subject,
        message,
        'noreply@betatrax.com',
        [instance.Email],
        fail_silently=True,
    )

def notify_all_duplicates(parent_instance):
    """
    Recursively update and notify all reports marked as duplicates of the parent_instance.
    """
    for duplicate in parent_instance.duplicates.all():
        # Sync the duplicate report's status with the parent
        duplicate.Status = parent_instance.Status
        duplicate.save(update_fields=['Status'])

        # Notify the tester with explicit duplicate phrasing
        send_status_update_email(duplicate, is_created=False, is_duplicate_update=True)
        
        # Recursively handle nested duplicates
        if duplicate.duplicates.exists():
            notify_all_duplicates(duplicate)

@receiver(post_save, sender=DefectReport)
def notify_tester(sender, instance, created, **kwargs):
    """
    Primary signal handler for tester notifications and duplicate propagation.
    """
    old_status = getattr(instance, '_old_status', None)
    
    # Check for new reports or specific status changes
    if created or (old_status and old_status != instance.Status):
        # 1. Notify the primary reporter
        send_status_update_email(instance, created)

        # 2. Propagate the status change to all duplicate reports
        if not created and old_status != instance.Status:
            notify_all_duplicates(instance)

@receiver(post_save, sender=DefectReport)
def generate_retest_record(sender, instance, created, **kwargs):
    """
    Automatic generation of retest placeholders when a status hits 'Fixed'.
    """
    if instance.Status == 'Fixed':
        if not Result.objects.filter(report_id=str(instance.id)).exists():
            Result.objects.create(
                report_id=str(instance.id),
                retest_result='Pending Retest',
                author=instance.assigned_to
            )

@receiver(pre_save, sender=DefectReport)
def track_old_status(sender, instance, **kwargs):
    """
    Snapshot of the status before saving to detect transitions in post_save.
    """
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_status = old_instance.Status
            instance._old_assigned_to = old_instance.assigned_to
        except sender.DoesNotExist:
            instance._old_status = None
            instance._old_assigned_to = None
    else:
        instance._old_status = None
        instance._old_assigned_to = None

@receiver(post_save, sender=DefectReport)
def update_developer_metrics(sender, instance, created, **kwargs):
    """
    Triggers metric updates based on status transitions.
    """
    old_status = getattr(instance, '_old_status', None)
    old_assigned_to = getattr(instance, '_old_assigned_to', None)
    apply_status_transition_metrics(
        instance=instance,
        old_status=old_status,
        old_assigned_to=old_assigned_to,
    )