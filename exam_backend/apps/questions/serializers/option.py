"""
选项序列化器
"""
from rest_framework import serializers

from apps.questions.models import Option


class OptionSerializer(serializers.ModelSerializer):
    """
    选项序列化器
    """

    class Meta:
        model = Option
        fields = ['id', 'label', 'content', 'is_correct', 'order']
        read_only_fields = ['id']


class OptionCreateSerializer(serializers.ModelSerializer):
    """
    选项创建序列化器
    """

    class Meta:
        model = Option
        fields = ['label', 'content', 'is_correct', 'order']


class OptionDisplaySerializer(serializers.ModelSerializer):
    """
    选项展示序列化器（不显示是否正确，用于考试）
    """

    class Meta:
        model = Option
        fields = ['id', 'label', 'content', 'order']
