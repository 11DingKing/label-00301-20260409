"""
答题记录序列化器
"""
from rest_framework import serializers

from apps.submissions.models import Answer
from apps.questions.serializers.question import QuestionExamSerializer


class AnswerSerializer(serializers.ModelSerializer):
    """
    答题记录序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    question_number = serializers.IntegerField(source='paper_question.question_number', read_only=True)
    max_score = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'submission', 'paper_question', 'question_number',
            'answer_content', 'answer_files', 'status', 'status_display',
            'is_marked', 'score', 'max_score', 'is_correct',
            'comment', 'graded_at',
            'first_answer_time', 'last_answer_time', 'answer_duration',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'score', 'is_correct', 'comment', 'graded_at',
            'created_at', 'updated_at'
        ]


class AnswerDetailSerializer(serializers.ModelSerializer):
    """
    答题记录详情序列化器（包含题目信息）
    """
    question = QuestionExamSerializer(source='paper_question.question', read_only=True)
    question_number = serializers.IntegerField(source='paper_question.question_number', read_only=True)
    max_score = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'submission', 'paper_question', 'question', 'question_number',
            'answer_content', 'answer_files', 'status', 'status_display',
            'is_marked', 'score', 'max_score', 'is_correct',
            'comment', 'graded_at',
            'created_at', 'updated_at'
        ]


class AnswerResultSerializer(serializers.ModelSerializer):
    """
    答题结果序列化器（考试结束后显示）
    """
    question_number = serializers.IntegerField(source='paper_question.question_number', read_only=True)
    question_title = serializers.CharField(source='paper_question.question.title', read_only=True)
    question_type = serializers.CharField(source='paper_question.question.type', read_only=True)
    correct_answer = serializers.CharField(source='paper_question.question.answer', read_only=True)
    answer_analysis = serializers.CharField(source='paper_question.question.answer_analysis', read_only=True)
    max_score = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'question_number', 'question_title', 'question_type',
            'answer_content', 'correct_answer', 'answer_analysis',
            'score', 'max_score', 'is_correct', 'comment'
        ]
