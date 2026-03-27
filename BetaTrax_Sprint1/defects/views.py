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
