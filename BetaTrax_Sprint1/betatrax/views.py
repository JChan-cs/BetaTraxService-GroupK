from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import DefectReport

@login_required
def assigned_defects_list(request):
    defects = DefectReport.objects.filter(assigned_to=request.user, status='ASSIGNED')
    return render(request, 'betatrax/assigned_defects.html', {'defects': defects})

@login_required
def new_defects_list(request):
    """Show all defect reports with status 'NEW' for evaluation."""
    defects = DefectReport.objects.filter(status='NEW')
    return render(request, 'betatrax/new_defects.html', {'defects': defects})
