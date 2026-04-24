"""
Views for Developer role - view assigned defects and submit fixes
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from drf_spectacular.utils import extend_schema
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import DefectReport
from .serializers import DefectReportSerializer
from comments.models import Comment


class DeveloperViewsMixin:
    """Mixin providing developer-specific actions"""

    @action(detail=False, methods=['get'], url_path='my-tasks', permission_classes=[IsAuthenticated])
    def my_tasks(self, request):
        """List all defects assigned to the current developer"""
        if not request.user.groups.filter(name='Developer').exists():
            error_msg = "Only Developers can view their task list."
            if request.accepted_renderer.format == 'json':
                return Response({"detail": error_msg}, status=status.HTTP_403_FORBIDDEN)
            messages.error(request, error_msg)
            return redirect('defectreport-list')
        
        # Get defects assigned to current developer
        defects = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(defects, many=True)
        
        if request.accepted_renderer.format == 'html':
            context = {'defects': defects, 'title': 'My Developer Tasks'}
            return render(request, 'defects/developer_task_list.html', context)
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='open', permission_classes=[IsAuthenticated])
    def open_defects(self, request):
        """List all 'Open' defects available for developers to pick up"""
        if not request.user.groups.filter(name='Developer').exists():
            error_msg = "Only Developers can view open defects."
            if request.accepted_renderer.format == 'json':
                return Response({"detail": error_msg}, status=status.HTTP_403_FORBIDDEN)
            messages.error(request, error_msg)
            return redirect('defectreport-list')
        
        # Get only Open defects (not yet assigned)
        defects = self.get_queryset().filter(Status='Open', assigned_to__isnull=True)
        serializer = self.get_serializer(defects, many=True)
        
        if request.accepted_renderer.format == 'html':
            context = {'defects': defects, 'title': 'Open Defects Available'}
            return render(request, 'defects/open_defects.html', context)
        
        return Response(serializer.data)

    @extend_schema(summary="Assign defect to current developer")
    @action(detail=True, methods=['patch'], url_path='assign', permission_classes=[IsAuthenticated])
    def assign_to_me(self, request, pk=None):
        """Developer claims/takes a defect to work on"""
        defect = self.get_object()
        
        if not request.user.groups.filter(name='Developer').exists():
            return Response(
                {"detail": "Only Developers can take defects."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Only unassigned Open defects can be taken
        if defect.Status != 'Open':
            return Response(
                {"error": f"Only 'Open' defects can be taken. Current status: {defect.Status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if defect.assigned_to is not None:
            return Response(
                {"error": f"This defect is already assigned to {defect.assigned_to.username}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Assign to current developer
        defect.assigned_to = request.user
        defect.Status = 'Assigned'
        defect.save()
        
        serializer = self.get_serializer(defect)
        success_msg = f"Defect #{defect.id} has been assigned to you."
        
        if request.accepted_renderer.format == 'json':
            return Response({
                "message": success_msg,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        messages.success(request, success_msg)
        return redirect('defectreport-detail', pk=defect.pk)

    @extend_schema(summary="Submit defect fix", methods=['POST'])
    @action(detail=True, methods=['get', 'post'], url_path='fix', permission_classes=[IsAuthenticated])
    def fix_defect(self, request, pk=None):
        """Developer view for fixing an assigned defect"""
        defect = self.get_object()
        
        if not request.user.groups.filter(name='Developer').exists():
            error_msg = "Only Developers can fix defects."
            if request.accepted_renderer.format == 'json':
                return Response({"detail": error_msg}, status=status.HTTP_403_FORBIDDEN)
            messages.error(request, error_msg)
            return redirect('defectreport-detail', pk=defect.pk)
        
        # Only assigned defects can be fixed
        if defect.Status != 'Assigned':
            error_msg = f"This defect is {defect.Status.lower()} and cannot be fixed right now."
            if request.accepted_renderer.format == 'json':
                return Response({"detail": error_msg}, status=status.HTTP_400_BAD_REQUEST)
            messages.error(request, error_msg)
            return redirect('defectreport-detail', pk=defect.pk)
        
        # Verify developer owns the task
        if defect.assigned_to != request.user:
            error_msg = "You can only fix defects assigned to you."
            if request.accepted_renderer.format == 'json':
                return Response({"detail": error_msg}, status=status.HTTP_403_FORBIDDEN)
            messages.error(request, error_msg)
            return redirect('defectreport-detail', pk=defect.pk)
        
        if request.method == 'POST':
            fix_notes = request.data.get('fix_notes', '')
            
            if not fix_notes:
                error_msg = "Please provide details about your fix."
                if request.accepted_renderer.format == 'json':
                    return Response(
                        {"detail": error_msg},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                messages.error(request, error_msg)
            else:
                # Mark defect as Resolved
                defect.Status = 'Resolved'
                defect.save()
                
                success_msg = f"Defect #{defect.id} marked as Resolved. Product Owner will retest it."
                if request.accepted_renderer.format == 'json':
                    return Response({
                        "message": success_msg,
                        "status": defect.Status
                    }, status=status.HTTP_200_OK)
                
                messages.success(request, success_msg)
                return redirect('defectreport-fix-success', pk=defect.pk)
        
        comments = Comment.objects.filter(defect=defect).order_by('-created_at')[:50]
        
        context = {
            'defect': defect,
            'comments': comments,
            'title': f'Fix Defect #{defect.id}'
        }
        return render(request, 'defects/defect_fix_view.html', context)

    @action(detail=True, methods=['get'], url_path='fix-success', renderer_classes=[TemplateHTMLRenderer])
    def fix_success(self, request, pk=None):
        """Success page after submitting fix"""
        defect = self.get_object()
        context = {'defect': defect}
        return render(request, 'defects/fix_success.html', context)
