"""
提交记录序列化器
"""
from rest_framework import serializers

from apps.submissions.models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    """
    提交记录序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    is_passed = serializers.BooleanField(read_only=True)
    duration_seconds = serializers.IntegerField(read_only=True)
    remaining_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id', 'exam', 'exam_title', 'user', 'user_name',
            'status', 'status_display', 'attempt',
            'start_time', 'submit_time', 'end_time',
            'score', 'objective_score', 'subjective_score', 'is_passed',
            'switch_count', 'duration_seconds', 'remaining_time',
            'created_at'
        ]
