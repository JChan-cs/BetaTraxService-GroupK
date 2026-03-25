from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from .models import DefectReport
from .serializers import DefectReportSerializer

class DefectReportViewSet(viewsets.ModelViewSet):
  queryset = DefectReport.objects.all()
  serializer_class =  DefectReportSerializer
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
    
