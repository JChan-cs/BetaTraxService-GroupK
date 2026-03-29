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
  @action(detail = True, methods = ["patch"], url_path = "status", permission_classes = [IsAuthenticated])
  def change_status(self, request, pk = None):
    defect = self.get_object()
    serializer = DefectReportStatusSerializer(
      defect,
      data = request.data,
      context = {"request": request},
      partial = True,
    )
    serializer.is_valid(raise_exception = True)
    serializer.save()
    return Response(
      {
        "message": f"Defect status updated to {defect.Status}.",
        "data": serializer.data,
      },
      status = status.HTTP_200_OK,
    )


  @action(detail=True, methods=["get", "post"], url_path="evaluate", 
          renderer_classes=[JSONRenderer, TemplateHTMLRenderer],
          permission_classes=[IsAuthenticatedOrReadOnly])
  def evaluate(self, request, pk=None):
    defect = self.get_object()

    if request.method == 'POST':
        # 1. Manually extract which button was clicked
        mutable_data = request.data.copy()
        if 'accept' in request.data:
            mutable_data['action'] = 'accept'
        elif 'reject' in request.data:
            mutable_data['action'] = 'reject'
        elif 'duplicate' in request.data:
            mutable_data['action'] = 'duplicate'

        # 2. Pass the modified data to the serializer
        serializer = DefectEvaluationSerializer(defect, data=mutable_data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            
            # Use the new 'action' to set the message
            action_taken = mutable_data.get('action')
            msg_map = {
                'accept': f"Report #{defect.id} successfully opened.",
                'reject': f"Report #{defect.id} rejected.",
                'duplicate': f"Report #{defect.id} marked as duplicate."
            }
            messages.success(request, msg_map.get(action_taken, "Update successful."))
            
            # Correct redirect name (using the basename from your error log)
            return redirect('defectreport-evaluate-success', pk=defect.pk)
          
          # If invalid, stay on page to show errors
        comments = Comment.objects.all().order_by('-created_at')[:50]
        return Response({
            'defect': defect,           
            'comments': comments,       
            'errors': serializer.errors,
            'form_data': mutable_data,
            'severity_choices': DefectReport.SeverityC,
            'priority_choices': DefectReport.PriorityC
        }, template_name='defect_evaluation.html')

    # GET logic...
    comments = Comment.objects.all().order_by('-created_at')[:50]
    return Response({'defect': defect, 'comments': comments, 'severity_choices': DefectReport.SeverityC, 'priority_choices': DefectReport.PriorityC}, template_name='defect_evaluation.html')

  @action(detail=True, methods=["get"], url_path="evaluate/success", renderer_classes=[TemplateHTMLRenderer])
  def evaluate_success(self, request, pk=None):
      """Dedicated page to show the success state after triage."""
      defect = self.get_object()
      return Response({'defect': defect}, template_name='evaluation_success.html')