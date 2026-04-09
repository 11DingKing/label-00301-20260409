"""
阅卷序列化器
"""
from rest_framework import serializers

from apps.grading.models import GradingTask
from apps.submissions.models import Answer


class GradingTaskSerializer(serializers.ModelSerializer):
    """
    阅卷任务序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    grader_name = serializers.CharField(source='grader.username', read_only=True)
    progress = serializers.FloatField(read_only=True)

    class Meta:
        model = GradingTask
        fields = [
            'id', 'exam', 'exam_title', 'grader', 'grader_name',
            'question', 'status', 'status_display',
            'total_count', 'graded_count', 'progress',
            'assigned_at', 'completed_at', 'created_at'
        ]


class GradeAnswerSerializer(serializers.Serializer):
    """
    批改答案序列化器
    """
    answer_id = serializers.IntegerField()
    score = serializers.DecimalField(max_digits=5, decimal_places=1)
    comment = serializers.CharField(required=False, allow_blank=True)


class BatchGradeSerializer(serializers.Serializer):
    """
    批量批改序列化器
    """
    grades = GradeAnswerSerializer(many=True)


class AnswerToGradeSerializer(serializers.ModelSerializer):
    """
    待批改答案序列化器
    """
    question_title = serializers.CharField(source='paper_question.question.title', read_only=True)
    question_type = serializers.CharField(source='paper_question.question.type', read_only=True)
    correct_answer = serializers.CharField(source='paper_question.question.answer', read_only=True)
    max_score = serializers.DecimalField(source='paper_question.score', max_digits=5, decimal_places=1, read_only=True)
    user_name = serializers.CharField(source='submission.user.username', read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'submission', 'paper_question',
            'question_title', 'question_type', 'correct_answer',
            'answer_content', 'answer_files',
            'score', 'max_score', 'comment', 'user_name',
            'status', 'created_at'
        ]
