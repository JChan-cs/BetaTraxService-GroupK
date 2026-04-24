from rest_framework import serializers
from .models import Result

class ResolvingSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username', help_text="The username of the user who created this resolving result.")

    class Meta:
        model = Result
        fields = ['id', 'report_id', 'date', 'retest_result', 'author']
        read_only_fields = ['author', 'date']