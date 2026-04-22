from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import DefectReport
from .developer_metrics import apply_status_transition_metrics
from Resolving.models import Result

@receiver(post_save, sender=DefectReport)
def notify_tester(sender, instance, created, **kwargs):
    # Only proceed if the report has an email address
    if not instance.Email:
        return

    if created:
        subject = f"BetaTrax: New Report Submitted - {instance.ReportTitle}"
        message = (
            f"Hello,\n\n"
            f"Your report #{instance.id} has been received.\n"
            f"Status: {instance.Status}\n\n"
            f"A Product Owner will evaluate it shortly."
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

@receiver(post_save, sender=DefectReport)
def generate_retest_record(sender, instance, created, **kwargs):
    if instance.Status == 'Fixed':
        if not Result.objects.filter(report_id = str(instance.id)).exists():
            
            Result.objects.create(
                report_id = str(instance.id),
                retest_result = 'Pending Retest',
                author= instance.assigned_to
            )

@receiver(pre_save, sender=DefectReport)
def track_old_status(sender, instance, **kwargs):
    """Store old status/assignee before saving for transition-aware metrics."""
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
    """Update fixed/reopened counts when status changes."""
    old_status = getattr(instance, '_old_status', None)
    old_assigned_to = getattr(instance, '_old_assigned_to', None)
    apply_status_transition_metrics(
        instance=instance,
        old_status=old_status,
        old_assigned_to=old_assigned_to,
    )