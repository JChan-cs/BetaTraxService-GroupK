from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    """A comment made by a user on a defect report."""
    author = serializers.ReadOnlyField(
        source='author.username',
        help_text="The username of the comment's author."
    )

    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'created_at']
        read_only_fields = ['author', 'created_at']
        