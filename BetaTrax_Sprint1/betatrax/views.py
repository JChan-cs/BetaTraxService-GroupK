from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
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

@api_view(['PATCH'])
def fix_defect(request, pk):
    defect = get_object_or_404(DefectReport, pk=pk)
    
    if defect.status != 'ASSIGNED':
        return Response({'error': 'Defect must be in ASSIGNED status to be fixed.'}, status=400)