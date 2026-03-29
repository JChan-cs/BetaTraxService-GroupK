from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from .models import DefectReport
from comments.models import Comment
from .serializers import DefectReportSerializer, DefectReportStatusSerializer, DefectEvaluationSerializer
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer



class DefectReportViewSet(viewsets.ModelViewSet):
    queryset = DefectReport.objects.all()
    serializer_class =  DefectReportSerializer
    # renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    search_fields = ["ReportTitle", "TesterID"]

    def get_queryset(self):
        queryset = DefectReport.objects.all()
        TargetedStatus = self.request.query_params.get("Status")
        if TargetedStatus is not None:
            queryset = queryset.filter(Status = TargetedStatus)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data["Status"] = "New"
        serializers =  self.get_serializer(data = request.data)
        serializers.is_valid(raise_exception = True)
        self.perform_create(serializers)
        return Response(serializers.data, status = status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
        permission_classes=[IsAuthenticated],
        renderer_classes=[TemplateHTMLRenderer, JSONRenderer]
    )
    def change_status(self, request, pk=None):
        defect = self.get_object()
        serializer = DefectReportStatusSerializer(
            defect,
            data=request.data,
            context={"request": request},
            partial=True,
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
  
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        user = request.user
        links = []
        role = "Anonymous"
        if user.is_authenticated:
            if user.groups.filter(name='Tester').exists():
                role = "Tester"
                links = [
                    {"name": "Submit Defect Report", "url": "/api/reports/", "method": "POST"},
                    {"name": "My Submissions", "url": f'/api/reports/?tester_id={user.id}', "method": "GET"},]
            elif user.groups.filter(name='ProductOwner').exists():
                role = "Product Owner"
                links = [{'name': 'New Reports (Pending Evaluation)', 'url': '/api/reports/?Status=New', "method": "GET"},
                    {"name": "Open Defects (Ready to Assign)", "url": '/api/reports/?Status=Open', "method": "GET"},
                    {"name": "All Reports", 'url': '/api/reports/', "method": "GET"},
                ]
            elif user.groups.filter(name='Developer').exists():
                role = 'Developer'
                links = [{"name": "My Assigned Tasks", "url": "/api/reports/?Status=Assigned", "method": "GET"},{"name": "Open Defects (Available)", 'url': '/api/reports/?Status=Open', "method": 'GET'},]
            else:
                role = 'Authenticated User (No Role)'
                links = [{"name": "View All Reports", 'url': '/api/reports/', 'method': 'GET'},]
        else:
            links = [{"name": "Login", "url": "/admin/login/", "method": "GET"},
                {"name": "View All Reports (Read Only)", "url": "/api/reports/", "method": "GET"},]
      
        return Response({'username': user.username if user.is_authenticated else 'Not logged in','role': role,'links': links,})
  
    @action(detail=True, methods=['patch'], url_path='accept')
    def accept(self, request, pk=None):
        defect = self.get_object()
        
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
        defect = self.get_object()

        if request.method == 'POST':
            # 1. Product Owner Group Check
            if not request.user.groups.filter(name='ProductOwner').exists():
                error_msg = "Only Product Owners can evaluate reports."
                if request.accepted_renderer.format == 'json':
                    return Response({"detail": error_msg}, status=status.HTTP_403_FORBIDDEN)
                messages.error(request, error_msg)
                return redirect('defectreport-detail', pk=defect.pk)

            # 2. Normalize data for the Serializer
            mutable_data = request.data.copy()
            if 'accept' in request.data: mutable_data['action'] = 'accept'
            elif 'reject' in request.data: mutable_data['action'] = 'reject'
            elif 'duplicate' in request.data: mutable_data['action'] = 'duplicate'
            
            serializer = DefectEvaluationSerializer(defect, data=mutable_data, context={'request': request})
            
            if serializer.is_valid():
                serializer.save()
                
                # 3. Hybrid Response (JSON for HTTPie, Redirect for Browser)
                if request.accepted_renderer.format == 'json':
                    return Response({
                        "message": f"Report #{defect.id} successfully updated.",
                        "status": defect.Status
                    }, status=status.HTTP_200_OK)

                messages.success(request, f"Report #{defect.id} updated.")
                return redirect('defectreport-evaluate-success', pk=defect.pk)

            # If invalid, handle errors for JSON vs HTML
            if request.accepted_renderer.format == 'json':
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            comments = Comment.objects.all().order_by('-created_at')[:50]
            context = {'defect': defect, 'comments': comments, 'errors': serializer.errors, 'severity_choices': DefectReport.SeverityC, 'priority_choices': DefectReport.PriorityC}
            return render(request, 'defect_evaluation.html', context)
        
    @action(detail=True, methods=["get"], url_path="evaluate-success", renderer_classes=[TemplateHTMLRenderer])
    def evaluate_success(self, request, pk=None):
        defect = self.get_object()
        return render(request, 'evaluation_success.html', context)
        # GET logic
        comments = Comment.objects.all().order_by('-created_at')[:50]
        context = {'defect': defect, 'comments': comments, 'severity_choices': DefectReport.SeverityC, 'priority_choices': DefectReport.PriorityC}
        return render(request, 'defect_evaluation.html', {'defect': defect})

    @action(detail=False, methods=['get'], url_path='open', renderer_classes=[TemplateHTMLRenderer, JSONRenderer])
    def open_defects(self, request):
        defects = DefectReport.objects.filter(Status='Open')
        if request.accepted_renderer.format == 'json':
            serializer = self.get_serializer(defects, many=True)
            return Response(serializer.data) # Returns clean JSON
        return render(request, 'open_defects.html', {'defects': defects})

    @action(detail=True, methods=['post'], url_path='take', permission_classes=[IsAuthenticated], renderer_classes=[TemplateHTMLRenderer, JSONRenderer])
    def take(self, request, pk=None):
        defect = self.get_object()
        # 1. CHECK FOR ERRORS FIRST
        is_not_open = defect.Status != 'Open'
        is_not_developer = not request.user.groups.filter(name='Developer').exists()

        if is_not_open or is_not_developer:
            error_msg = 'Cannot take this defect.'
            if is_not_open: error_msg += " Status is not Open."
            if is_not_developer: error_msg += " You are not in the Developer group."

            # 2. IF IT'S HTTPIE, SEND JSON ERROR INSTEAD OF REDIRECT
            if request.accepted_renderer.format == 'json':
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
            # For the browser, keep the redirect
            messages.error(request, error_msg)
            return redirect('defectreport-open-defects')

        # 3. SUCCESS LOGIC
        defect.assigned_to = request.user
        defect.Status = 'Assigned'
        defect.save()
        
        if request.accepted_renderer.format == 'json':
            serializer = self.get_serializer(defect)
            return Response(serializer.data)
        
        Comment.objects.create(author=request.user, text=f"Defect #{defect.id} assigned to {request.user.username}.")
        messages.success(request, "Success! Defect assigned.")
        return render(request, 'defects/take_success.html', {'defect': defect})
    @action(detail=False, methods=['get'], url_path='new', permission_classes=[IsAuthenticated])
    def new_defects(self, request):
        """API endpoint for Product Owner: list all defects with Status='New'."""
        defects = self.get_queryset().filter(Status='New')
        serializer = self.get_serializer(defects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my-assigned', permission_classes=[IsAuthenticated])
    def my_assigned_defects(self, request):
        """API endpoint for Developer: list defects assigned to current user with Status='Assigned'."""
        defects = self.get_queryset().filter(assigned_to=request.user, Status='Assigned')
        serializer = self.get_serializer(defects, many=True)
        return Response(serializer.data)