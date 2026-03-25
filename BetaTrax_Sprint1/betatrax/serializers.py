from rest_framework import serializers

class DefectReportSerializer(serializers.Serializer):
    report_id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    status = serializers.CharField(max_length=20, read_only=True)