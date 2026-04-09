"""
统计序列化器
"""
from rest_framework import serializers

from apps.statistics.models import ExamStatistics, UserStatistics


class ExamStatisticsSerializer(serializers.ModelSerializer):
    """
    考试统计序列化器
    """
    exam_title = serializers.CharField(source='exam.title', read_only=True)

    class Meta:
        model = ExamStatistics
        fields = [
            'id', 'exam', 'exam_title',
            'participant_count', 'submitted_count', 'graded_count',
            'average_score', 'highest_score', 'lowest_score', 'median_score',
            'pass_rate', 'score_distribution', 'question_stats',
            'created_at', 'updated_at'
        ]


class UserStatisticsSerializer(serializers.ModelSerializer):
    """
    用户统计序列化器
    """
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserStatistics
        fields = [
            'id', 'user', 'user_name',
            'exam_count', 'passed_count', 'total_score', 'average_score',
            'question_count', 'correct_count', 'accuracy_rate',
            'total_duration', 'weak_tags',
            'created_at', 'updated_at'
        ]


class ExamRankingSerializer(serializers.Serializer):
    """
    考试排名序列化器
    """
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    score = serializers.DecimalField(max_digits=6, decimal_places=1)
    duration = serializers.IntegerField()
    submit_time = serializers.DateTimeField()


class QuestionAnalysisSerializer(serializers.Serializer):
    """
    题目分析序列化器
    """
    question_id = serializers.IntegerField()
    question_number = serializers.IntegerField()
    question_title = serializers.CharField()
    question_type = serializers.CharField()
    total_count = serializers.IntegerField()
    correct_count = serializers.IntegerField()
    correct_rate = serializers.FloatField()
    average_score = serializers.FloatField()
    score_distribution = serializers.DictField()
