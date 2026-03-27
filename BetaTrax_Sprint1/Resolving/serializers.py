from rest_framework import serializers
from .models import Result

class ResolvingSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Result
        # Including the specific fields you requested for the report list
        fields = ['id', 'report_id', 'date', 'retest_result', 'author']
        read_only_fields = ['author', 'date']