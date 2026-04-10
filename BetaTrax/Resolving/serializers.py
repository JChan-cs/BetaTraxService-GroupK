# Unused API also kept for now

from rest_framework import serializers
from .models import Result

class ResolvingSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Result
        fields = ['id', 'report_id', 'date', 'retest_result', 'author']
        read_only_fields = ['author', 'date']