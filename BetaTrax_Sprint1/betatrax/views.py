from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import DefectReport
from .serializers import DefectReportSerializer

@login_required
def assigned_defects_list(request):
    defects = DefectReport.objects.filter(assigned_to=request.user, status='ASSIGNED')
    return render(request, 'betatrax/assigned_defects.html', {'defects': defects})

@login_required
def new_defects_list(request):
    """Show all defect reports with status 'NEW' for evaluation."""
    defects = DefectReport.objects.filter(status='NEW')
    return render(request, 'betatrax/new_defects.html', {'defects': defects})

@login_required
@api_view(['PATCH'])
def fix_defect(request, pk):
    defect = get_object_or_404(DefectReport, pk=pk)
    
    if defect.status != 'ASSIGNED':
        return Response({'error': 'Defect must be in ASSIGNED status to be fixed.'}, status=status.HTTP_400_BAD_REQUEST)
    
    defect.status = 'FIXED'
    defect.save()
    
    defect_serializer = DefectReportSerializer(defect)
    return Response(defect_serializer.data, status=status.HTTP_200_OK)

@login_required
@api_view(['PATCH'])
def resolve_defect(request, pk):
    defect = get_object_or_404(DefectReport, pk=pk)
    
    if defect.status != 'FIXED':
        return Response({'error': 'Defect must be in FIXED status to be resolved.'}, status=status.HTTP_400_BAD_REQUEST)
    
    defect.status = 'RESOLVED'
    defect.save()
    
    defect_serializer = DefectReportSerializer(defect)
    return Response(defect_serializer.data, status=status.HTTP_200_OK)