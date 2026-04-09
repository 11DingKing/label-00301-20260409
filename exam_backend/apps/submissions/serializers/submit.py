"""
提交相关序列化器
"""
from rest_framework import serializers


class AnswerSubmitSerializer(serializers.Serializer):
    """
    提交答案序列化器
    """
    paper_question_id = serializers.IntegerField()
    answer_content = serializers.CharField(allow_blank=True, required=False)
    answer_files = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    is_marked = serializers.BooleanField(required=False, default=False)


class BatchAnswerSubmitSerializer(serializers.Serializer):
    """
    批量提交答案序列化器
    """
    answers = AnswerSubmitSerializer(many=True)


class ExamSubmitSerializer(serializers.Serializer):
    """
    提交考试序列化器
    """
    answers = AnswerSubmitSerializer(many=True, required=False)
