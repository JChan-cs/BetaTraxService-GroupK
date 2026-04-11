"""
Views for Product Owner Confirm role - evaluate and accept/reject new defect reports
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import DefectReport
from .serializers import DefectReportStatusSerializer, DefectEvaluationSerializer
from comments.models import Comment


class ProductOwnerConfirmViewsMixin:
    """Mixin providing Product Owner Confirm-specific actions for initial defect evaluation"""

    @action(detail=True, methods=['patch'], url_path='accept', permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        """Product Owner accepts a new defect report and sets severity/priority"""
        defect = self.get_object()
        
        if not request.user.groups.filter(name='ProductOwner').exists():
            return Response(
                {"detail": "Only Product Owners can accept reports."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if defect.Status != 'New':
            return Response(
                {"error": 'Only New reports can be accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        severity = request.data.get("Severity")
        priority = request.data.get("Priority")
        if not severity or not priority:
            return Response(
                {'error': 'Severity and Priority are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        defect.Status = "Open"
        defect.Severity = severity
        defect.Priority = priority
        defect.save()
        
        return Response(
            {
                "status": 'accepted',
                "id": defect.id,
                "Severity": defect.Severity,
                "Priority": defect.Priority,
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get", "post"], url_path="evaluate", permission_classes=[IsAuthenticatedOrReadOnly])
    def evaluate(self, request, pk=None):
        """Product Owner evaluates a new defect report (accept/reject/mark duplicate)"""
        defect = self.get_object()
        serializer = None

        if request.method == 'POST':
            if not request.user.groups.filter(name='ProductOwner').exists():
                error_msg = "Only Product Owners can evaluate reports."
                if request.accepted_renderer.format == 'json':
                    return Response({"detail": error_msg}, status=status.HTTP_403_FORBIDDEN)
                messages.error(request, error_msg)
                return redirect('defectreport-detail', pk=defect.pk)
            
            mutable_data = request.data.copy()
            if 'accept' in request.data: mutable_data['action'] = 'accept'
            elif 'reject' in request.data: mutable_data['action'] = 'reject'
            elif 'duplicate' in request.data: mutable_data['action'] = 'duplicate'
            
            serializer = DefectEvaluationSerializer(defect, data=mutable_data, context={'request': request})
            
            if serializer.is_valid():
                serializer.save()
                
                if request.accepted_renderer.format == 'json':
                    return Response({
                        "message": f"Report #{defect.id} successfully updated.",
                        "status": defect.Status
                    }, status=status.HTTP_200_OK)

                messages.success(request, f"Report #{defect.id} updated.")
                return redirect('defectreport-evaluate-success', pk=defect.pk)

            if request.accepted_renderer.format == 'json':
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            messages.error(request, "Please fix the errors below.")

        
        comments = Comment.objects.filter(defect=defect).order_by('-created_at')[:50]
        
        context = {
            'defect': defect, 
            'comments': comments, 
            'severity_choices': DefectReport.SeverityC, 
            'priority_choices': DefectReport.PriorityC,
            'errors': serializer.errors if serializer else None
        }
        return render(request, 'defects/defect_evaluation.html', context)
    
    @action(detail=True, methods=["get"], url_path="evaluate-success", renderer_classes=[TemplateHTMLRenderer])
    def evaluate_success(self, request, pk=None):
        """Success page after evaluation"""
        defect = self.get_object()
        context = {'defect': defect}
        return render(request, 'defects/evaluation_success.html', context)
