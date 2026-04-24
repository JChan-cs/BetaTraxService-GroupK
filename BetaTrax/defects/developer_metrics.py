from .models import DeveloperMetrics


def classify_effectiveness(defects_fixed, defects_reopened):
    if defects_fixed < 20:
        return "Insufficient data", None

    ratio = defects_reopened / defects_fixed
    if ratio < 1 / 32:
        rating = "Good"
    elif ratio < 1 / 8:
        rating = "Fair"
    else:
        rating = "Poor"

    return rating, round(ratio, 6)


def build_metrics_response(user, defects_fixed, defects_reopened):
    rating, ratio = classify_effectiveness(defects_fixed, defects_reopened)
    return {
        "user_id": user.id,
        "username": user.username,
        "defects_fixed": defects_fixed,
        "defects_reopened": defects_reopened,
        "ratio": ratio,
        "effectiveness": rating,
    }


def apply_status_transition_metrics(instance, old_status=None, old_assigned_to=None):
    new_status = instance.Status
    assigned_to = instance.assigned_to

    if assigned_to:
        DeveloperMetrics.objects.get_or_create(user=assigned_to)

    if new_status == "Fixed" and old_status != "Fixed":
        if not assigned_to:
            return

        metrics, _ = DeveloperMetrics.objects.get_or_create(user=assigned_to)
        metrics.defects_fixed += 1
        metrics.save()

    if new_status == "Reopened" and old_status != "Reopened":
        reopened_owner = old_assigned_to or assigned_to
        if not reopened_owner:
            return

        metrics, _ = DeveloperMetrics.objects.get_or_create(user=reopened_owner)
        metrics.defects_reopened += 1
        metrics.save()
