"""
Views for Product Owner Retest role - retest fixed defects and confirm resolution
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from drf_spectacular.utils import extend_schema
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import DefectReport
from .serializers import DefectReportStatusSerializer
from comments.models import Comment


class ProductOwnerRetestViewsMixin:
    """Mixin providing Product Owner Retest-specific actions for retesting fixed defects"""

    @extend_schema(summary="Submit defect retest outcome", description="Product Owner records a retest outcome (pass/fail) for a defect in 'Resolved' status.", methods=["POST"])
    @extend_schema(exclude=True, methods=["GET"])
    @action(
        detail=True,
        methods=["get", "post"],
        url_path="retest",
        permission_classes=[IsAuthenticatedOrReadOnly],
        renderer_classes=[TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer]
    )
    def retest(self, request, pk=None):
        """Product Owner retests a defect that has been fixed by a developer"""
        defect = self.get_object()
        
        # Only defects in 'Resolved' status can be retested
        if defect.Status != 'Resolved':
            error_msg = f"Only 'Resolved' defects can be retested. Current status: {defect.Status}"
            if request.accepted_renderer.format == 'json':
                return Response(
                    {"detail": error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            messages.error(request, error_msg)
            return redirect('defectreport-detail', pk=defect.pk)
        
        if request.method == 'POST':
            if not request.user.groups.filter(name='ProductOwner').exists():
                error_msg = "Only Product Owners can retest defects."
                if request.accepted_renderer.format == 'json':
                    return Response({"detail": error_msg}, status=status.HTTP_403_FORBIDDEN)
                messages.error(request, error_msg)
                return redirect('defectreport-detail', pk=defect.pk)
            
            action_type = request.data.get('action')
            
            if action_type == 'pass':
                # Defect is fixed - mark as Closed
                defect.Status = 'Closed'
                defect.save()
                success_msg = f"Defect #{defect.id} confirmed as fixed and closed."
                
                if request.accepted_renderer.format == 'json':
                    return Response({
                        "message": success_msg,
                        "status": defect.Status
                    }, status=status.HTTP_200_OK)
                
                messages.success(request, success_msg)
                return redirect('defectreport-retest-success', pk=defect.pk)
            
            elif action_type == 'fail':
                # Defect still has issues - reopen
                defect.Status = 'Open'
                defect.save()
                error_msg = f"Defect #{defect.id} reopened. Developer needs to address it again."
                
                if request.accepted_renderer.format == 'json':
                    return Response({
                        "message": error_msg,
                        "status": defect.Status
                    }, status=status.HTTP_200_OK)
                
                messages.warning(request, error_msg)
                return redirect('defectreport-detail', pk=defect.pk)
            
            else:
                error_msg = "Invalid action. Use 'pass' or 'fail'."
                if request.accepted_renderer.format == 'json':
                    return Response(
                        {"detail": error_msg},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                messages.error(request, error_msg)
        
        comments = Comment.objects.filter(defect=defect).order_by('-created_at')[:50]
        
        context = {
            'defect': defect,
            'comments': comments,
            'developer': defect.assigned_to
        }
        return render(request, 'defects/defect_retest.html', context)
    
    @extend_schema(exclude=True)
    @action(
        detail=True,
        methods=["get"],
        url_path="retest-success",
        renderer_classes=[TemplateHTMLRenderer]
    )
    def retest_success(self, request, pk=None):
        """Success page after retest confirmation"""
        defect = self.get_object()
        context = {'defect': defect}
        return render(request, 'defects/retest_success.html', context)

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
        permission_classes=[IsAuthenticated],
        renderer_classes=[TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer],
    )
    def change_status(self, request, pk=None):
        """Update defect status (for operational status changes)"""
        defect = self.get_object()
        
        if "Status" not in request.data:
            return Response(
                {"Status": "This field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.data.get("Status") == defect.Status:
            return Response(
                {"Status": f"Defect is already '{defect.Status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = DefectReportStatusSerializer(
            defect,
            data=request.data,
            context={"request": request},
            partial=False,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": f"Defect status updated to {defect.Status}.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
