from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from defects.models import DefectReport
from defects.serializers import DefectReportStatusSerializer


@login_required
def assigned_defects_list(request):
    defects = DefectReport.objects.filter(assigned_to=request.user, status="ASSIGNED")
    return render(request, "assigned/assigned_defects.html", {"defects": defects})


@login_required
def new_defects_list(request):
    """Show all defect reports with status 'NEW' for evaluation."""
    defects = DefectReport.objects.filter(status="NEW")
    return render(request, "assigned/new_defects.html", {"defects": defects})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_defect_status(request, pk):
    defect = get_object_or_404(DefectReport, pk=pk)

    serializer = DefectReportStatusSerializer(defect, data=request.data, context={"request": request}, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": f"Defect status updated to {defect.status}.", 
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
