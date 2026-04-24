from rest_framework import viewsets, permissions
from .models import Result
from .serializers import ResolvingSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

@extend_schema(tags=['resolving'])
@extend_schema_view(
    list=extend_schema(
        summary="List resolving results", 
        description="Retrieve a list of all resolving result entries ordered by newest first.",
        responses={
            200: OpenApiResponse(
                response=ResolvingSerializer(many=True),
                description="Resolving results retrieved successfully"
            )
        }
    ),
    create=extend_schema(
        summary="Create resolving result", 
        description="Create a new resolving result entry. User must be authenticated.",
        request=ResolvingSerializer,
        responses={
            201: OpenApiResponse(
                response=ResolvingSerializer,
                description="Resolving result created successfully"
            ),
            400: OpenApiResponse(description="Invalid input data"),
            403: OpenApiResponse(description="Authentication required for write operations")
        }
    ),
    retrieve=extend_schema(
        summary="Get resolving result", 
        description="Retrieve a single resolving result by its ID.",
        responses={
            200: OpenApiResponse(response=ResolvingSerializer, description="Resolving result retrieved successfully"),
            404: OpenApiResponse(description="Resolving result not found")
        }
    ),
    update=extend_schema(
        summary="Update resolving result", 
        description="Update an existing resolving result entry.",
        request=ResolvingSerializer,
        responses={
            200: OpenApiResponse(response=ResolvingSerializer, description="Resolving result fully updated successfully"),
            400: OpenApiResponse(description="Invalid input data"),
            403: OpenApiResponse(description="Authentication required for write operations"),
            404: OpenApiResponse(description="Resolving result not found")
        }

    ),
    partial_update=extend_schema(
        summary="Partially update resolving result", 
        description="Partially update an existing resolving result entry.",
        request=ResolvingSerializer,
        responses={
            200: OpenApiResponse(response=ResolvingSerializer, description="Resolving result partially updated successfully"),
            400: OpenApiResponse(description="Invalid input data"),
            403: OpenApiResponse(description="Authentication required for write operations"),
            404: OpenApiResponse(description="Resolving result not found")
        }
    ),
    destroy=extend_schema(
        summary="Delete resolving result", 
        description="Delete an existing resolving result entry.",
        responses={
            204: OpenApiResponse(description="Resolving result deleted successfully"),
            403: OpenApiResponse(description="Authentication required for write operations"),
            404: OpenApiResponse(description="Resolving result not found")
        }
    ),
)
class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.select_related('author').all().order_by('-date')
    serializer_class = ResolvingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)