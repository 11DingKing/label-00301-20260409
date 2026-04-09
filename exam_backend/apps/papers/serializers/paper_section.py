"""
试卷大题序列化器
"""
from rest_framework import serializers

from apps.papers.models import PaperSection
from apps.papers.serializers.paper_question import PaperQuestionSerializer


class PaperSectionSerializer(serializers.ModelSerializer):
    """
    试卷大题序列化器
    """
    paper_questions = PaperQuestionSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    section_score = serializers.DecimalField(max_digits=6, decimal_places=1, read_only=True)

    class Meta:
        model = PaperSection
        fields = [
            'id', 'title', 'description', 'question_type', 'order',
            'paper_questions', 'question_count', 'section_score'
        ]
