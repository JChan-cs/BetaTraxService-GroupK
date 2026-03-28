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