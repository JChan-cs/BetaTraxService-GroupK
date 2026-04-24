from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from .models import Comment
from .serializers import CommentSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List comments", 
        description="Retrieve a list of all comments ordered by newest first.",
        responses={
            200: OpenApiResponse(
                response=CommentSerializer(many=True),
                description="Comments retrieved successfully"
            )
        }
    ),
    create=extend_schema(
        summary="Create comment", 
        description="Create a new comment. User must be authenticated.",
        request=CommentSerializer,
        responses={
            201: OpenApiResponse(
                response=CommentSerializer,
                description="Comment created successfully"
            ),
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Permission denied")
        }
    ),
    retrieve=extend_schema(
        summary="Get comment", 
        description="Retrieve a single comment by its ID.",
        responses={
            200: OpenApiResponse(response=CommentSerializer, description="Comment retrieved successfully"),
            404: OpenApiResponse(description="Comment not found")
        }
    ),
    update=extend_schema(
        summary="Update comment", 
        description="Update an existing comment.",
        request=CommentSerializer,
        responses={
            200: OpenApiResponse(response=CommentSerializer, description="Comment fully updated successfully"),
            400: OpenApiResponse(description="Invalid input data"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Comment not found")
        }

    ),
    partial_update=extend_schema(
        summary="Partially update comment", 
        description="Partially update an existing comment.",
        request=CommentSerializer,
        responses={
            200: OpenApiResponse(response=CommentSerializer, description="Comment partially updated successfully"),
            400: OpenApiResponse(description="Invalid input data"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Comment not found")
        }
    ),
    destroy=extend_schema(
        summary="Delete comment", 
        description="Delete an existing comment.",
        responses={
            204: OpenApiResponse(description="Comment deleted successfully"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Comment not found")
        }
    ),
)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author').all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
