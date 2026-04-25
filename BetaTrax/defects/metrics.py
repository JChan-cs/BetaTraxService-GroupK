"""
Developer effectiveness metrics module.

Calculates and classifies developer effectiveness based on the ratio of
defects reopened vs. defects reported as fixed.
"""

from django.db.models import Q, Count
from .models import DefectReport


def get_developer_effectiveness(developer_user):
    """
    Calculate developer effectiveness metric.
    
    Args:
        developer_user: User object representing the developer
        
    Returns:
        dict: Contains 'classification' and 'details' with metrics
        
    Classification rules:
    - If defects fixed < 20: "Insufficient data"
    - If reopened/fixed ratio < 0.03125 (1/32): "Good"
    - If reopened/fixed ratio < 0.125 (1/8): "Fair"
    - Otherwise: "Poor"
    """
    # Count defects reported as fixed by this developer
    fixed_count = DefectReport.objects.filter(
        assigned_to=developer_user,
        Status='Fixed'
    ).count()
    
    # Count defects reopened for this developer
    reopened_count = DefectReport.objects.filter(
        assigned_to=developer_user,
        Status='Reopened'
    ).count()
    
    details = {
        'developer_id': developer_user.id,
        'developer_username': developer_user.username,
        'defects_fixed': fixed_count,
        'defects_reopened': reopened_count,
    }
    
    # Classification logic
    if fixed_count < 20:
        classification = "Insufficient data"
    else:
        ratio = reopened_count / fixed_count if fixed_count > 0 else 0
        
        if ratio < 0.03125:  # 1/32
            classification = "Good"
        elif ratio < 0.125:  # 1/8
            classification = "Fair"
        else:
            classification = "Poor"
        
        details['reopen_ratio'] = ratio
    
    return {
        'classification': classification,
        'details': details
    }
