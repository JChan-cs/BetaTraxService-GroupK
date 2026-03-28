from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import DefectReport
from .serializers import DefectReportSerializer, DefectReportStatusSerializer


class DefectReportViewSet(viewsets.ModelViewSet):
    queryset = DefectReport.objects.all()
    serializer_class = DefectReportSerializer
    search_fields = ["ReportTitle", "TesterID"]

    def get_queryset(self):
        queryset = DefectReport.objects.all()
        TargetedStatus = self.request.query_params.get("Status")
        if TargetedStatus is not None:
            queryset = queryset.filter(Status=TargetedStatus)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data["Status"] = "New"
        serializers = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        self.perform_create(serializers)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

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
            return Response:{"error": 'Only New reports can be accepted'},
        status=status.HTTP_400_BAD_REQUEST)
        severity = request.data.get("Severity")
        priority = request.data.get("Priority")
        if not severity or not priority:
            return Response(
                {'error': 'Severity and Priority are required'},
                status=status.HTTP_400_BAD_REQUEST)
            defect.Status = "Open"
            defect.Severity = severity
            defect.Priority = priority
            defect.save()
            return Response({
                "status": 'accepted',
                "id": defect.id,
                "Severity": defect.Severity,
                "Priority": defect.Priority,
            }, status=status.HTTP_200_OK)
