from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from defects.models import DefectReport
from defects.serializers import DefectReportStatusSerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, inline_serializer
from drf_spectacular.types import OpenApiTypes

@login_required
def assigned_defects_list(request):
    defects = DefectReport.objects.filter(
        assigned_to=request.user,
        Status='Assigned'          # note capital 'A'
    ).order_by('-CreatedTime')
    return render(request, "assigned/assigned_defects.html", {"defects": defects})

@login_required
def new_defects_list(request):
    defects = DefectReport.objects.filter(
        Status='New'               # capital 'N'
    ).order_by('-CreatedTime')
    return render(request, "assigned/new_defects.html", {"defects": defects})

@extend_schema(
    summary="Change defect status",
    description="Update the status of a defect report.",
    request=DefectReportStatusSerializer,
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Defect report ID',
            required=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="DefectStatusUpdateResponse",
                fields={
                    "message": serializers.CharField(),
                    "data": DefectReportStatusSerializer()
                }
            ),
            description="Defect status updated successfully",
        ), 
        400: OpenApiResponse(description="Invalid input data"),
        403: OpenApiResponse(description="Permission denied"),
        404: OpenApiResponse(description="Defect report not found"),},
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_defect_status(request, pk):
    defect = get_object_or_404(DefectReport, pk=pk)

    serializer = DefectReportStatusSerializer(defect, data=request.data, context={"request": request}, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": f"Defect status updated to {defect.Status}.", 
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
