from rest_framework import viewsets, permissions
from .models import Result
from .serializers import ResolvingSerializer

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.select_related('author').all().order_by('-date')
    serializer_class = ResolvingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)