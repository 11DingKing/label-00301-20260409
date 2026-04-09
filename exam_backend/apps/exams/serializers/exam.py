"""
考试序列化器
"""
from django.utils import timezone
from rest_framework import serializers

from apps.exams.models import Exam
from apps.papers.serializers import PaperListSerializer, PaperExamSerializer
from apps.submissions.models import Submission


class ExamListSerializer(serializers.ModelSerializer):
    """
    考试列表序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    paper_title = serializers.CharField(source='paper.title', read_only=True)
    actual_duration = serializers.IntegerField(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'description', 'type', 'type_display',
            'status', 'status_display', 'paper', 'paper_title',
            'start_time', 'end_time', 'is_time_limited', 'actual_duration',
            'max_attempts', 'is_public', 'participant_count', 'is_ongoing',
            'created_at'
        ]


class ExamDetailSerializer(serializers.ModelSerializer):
    """
    考试详情序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    paper = PaperListSerializer(read_only=True)
    actual_duration = serializers.IntegerField(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    submitted_count = serializers.IntegerField(read_only=True)
    is_started = serializers.BooleanField(read_only=True)
    is_ended = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'description', 'type', 'type_display',
            'status', 'status_display', 'paper', 'is_time_limited', 'duration',
            'start_time', 'end_time', 'actual_duration',
            'max_attempts', 'allow_late_submit', 'late_submit_minutes',
            'anti_cheat_enabled', 'fullscreen_required', 'switch_limit',
            'auto_publish_score', 'score_publish_time', 'is_public',
            'participant_count', 'submitted_count',
            'is_started', 'is_ended', 'is_ongoing',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]


class ExamCreateSerializer(serializers.ModelSerializer):
    """
    考试创建序列化器
    """

    class Meta:
        model = Exam
        fields = [
            'title', 'description', 'paper', 'type', 'status',
            'start_time', 'end_time', 'is_time_limited', 'duration', 'max_attempts',
            'allow_late_submit', 'late_submit_minutes',
            'anti_cheat_enabled', 'fullscreen_required', 'switch_limit',
            'auto_publish_score', 'score_publish_time', 'is_public'
        ]

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({'end_time': '结束时间必须晚于开始时间'})

        return attrs

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ExamStartSerializer(serializers.Serializer):
    """
    开始考试序列化器
    """
    exam_id = serializers.IntegerField()


class ExamPaperSerializer(serializers.ModelSerializer):
    """
    考试试卷序列化器（用于答题）
    """
    paper = PaperExamSerializer(read_only=True)
    remaining_time = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ['id', 'exam', 'paper', 'start_time', 'remaining_time', 'question_order']

    def get_remaining_time(self, obj):
        return obj.remaining_time
