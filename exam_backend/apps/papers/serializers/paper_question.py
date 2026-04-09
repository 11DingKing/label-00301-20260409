"""
试卷题目序列化器
"""
from rest_framework import serializers

from apps.papers.models import PaperQuestion
from apps.questions.serializers import QuestionListSerializer, QuestionExamSerializer


class PaperQuestionSerializer(serializers.ModelSerializer):
    """
    试卷题目序列化器
    """
    question = QuestionListSerializer(read_only=True)
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PaperQuestion
        fields = ['id', 'question', 'question_id', 'section', 'score', 'question_number', 'order']


class PaperQuestionExamSerializer(serializers.ModelSerializer):
    """
    考试用试卷题目序列化器（不显示答案）
    """
    question = QuestionExamSerializer(read_only=True)

    class Meta:
        model = PaperQuestion
        fields = ['id', 'question', 'score', 'question_number', 'order']


class PaperQuestionBatchSerializer(serializers.Serializer):
    """
    批量添加题目序列化器
    """
    question_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    section_id = serializers.IntegerField(required=False)
    score = serializers.DecimalField(max_digits=5, decimal_places=1, required=False)
