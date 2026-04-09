"""
试卷序列化器
"""
from rest_framework import serializers

from apps.papers.models import Paper
from apps.papers.serializers.paper_section import PaperSectionSerializer
from apps.papers.serializers.paper_question import PaperQuestionSerializer, PaperQuestionExamSerializer


class PaperListSerializer(serializers.ModelSerializer):
    """
    试卷列表序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Paper
        fields = [
            'id', 'title', 'description', 'total_score', 'pass_score',
            'time_limit', 'status', 'status_display', 'question_count',
            'created_by', 'created_by_name', 'created_at'
        ]


class PaperDetailSerializer(serializers.ModelSerializer):
    """
    试卷详情序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sections = PaperSectionSerializer(many=True, read_only=True)
    paper_questions = PaperQuestionSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    actual_total_score = serializers.DecimalField(max_digits=6, decimal_places=1, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Paper
        fields = [
            'id', 'title', 'description', 'total_score', 'actual_total_score',
            'pass_score', 'time_limit', 'status', 'status_display',
            'is_random_question', 'is_random_option',
            'show_answer_after_submit', 'allow_review',
            'sections', 'paper_questions', 'question_count',
            'category', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]


class PaperExamSerializer(serializers.ModelSerializer):
    """
    考试用试卷序列化器（不显示答案）
    """
    paper_questions = PaperQuestionExamSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Paper
        fields = [
            'id', 'title', 'description', 'total_score',
            'time_limit', 'is_random_question', 'is_random_option',
            'paper_questions', 'question_count'
        ]


class PaperCreateSerializer(serializers.ModelSerializer):
    """
    试卷创建序列化器
    """

    class Meta:
        model = Paper
        fields = [
            'title', 'description', 'total_score', 'pass_score',
            'time_limit', 'status', 'is_random_question', 'is_random_option',
            'show_answer_after_submit', 'allow_review', 'category'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
