"""
题目序列化器
"""
from rest_framework import serializers

from apps.questions.models import Question, Option, Attachment
from apps.questions.serializers.option import OptionSerializer, OptionDisplaySerializer
from apps.tags.serializers import TagSerializer, CategorySerializer


class AttachmentSerializer(serializers.ModelSerializer):
    """附件序列化器"""

    class Meta:
        model = Attachment
        fields = ['id', 'name', 'file', 'type', 'size', 'description']


class QuestionListSerializer(serializers.ModelSerializer):
    """
    题目列表序列化器
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'type', 'type_display',
            'difficulty', 'difficulty_display', 'score',
            'tags', 'use_count', 'correct_rate',
            'is_public', 'created_at'
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    """
    题目详情序列化器
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    options = OptionSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'type', 'type_display',
            'difficulty', 'difficulty_display', 'score',
            'content', 'answer', 'answer_analysis',
            'programming_language', 'time_limit', 'memory_limit', 'test_cases',
            'options', 'attachments', 'tags', 'category',
            'use_count', 'correct_count', 'correct_rate',
            'is_public', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]


class QuestionExamSerializer(serializers.ModelSerializer):
    """
    考试用题目序列化器（不显示答案）
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    options = OptionDisplaySerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'type', 'type_display',
            'content', 'score', 'options', 'attachments',
            'programming_language', 'time_limit', 'memory_limit'
        ]


class QuestionCreateSerializer(serializers.ModelSerializer):
    """
    题目创建序列化器
    """
    options = OptionSerializer(many=True, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Question
        fields = [
            'title', 'type', 'difficulty', 'score',
            'content', 'answer', 'answer_analysis',
            'programming_language', 'time_limit', 'memory_limit', 'test_cases',
            'options', 'tag_ids', 'category', 'is_public'
        ]

    def validate(self, attrs):
        question_type = attrs.get('type')

        # 选择题必须有选项
        if question_type in [Question.Type.SINGLE, Question.Type.MULTI]:
            options = attrs.get('options', [])
            if not options:
                raise serializers.ValidationError({'options': '选择题必须提供选项'})

            # 单选题只能有一个正确选项
            if question_type == Question.Type.SINGLE:
                correct_count = sum(1 for opt in options if opt.get('is_correct'))
                if correct_count != 1:
                    raise serializers.ValidationError({'options': '单选题必须有且只有一个正确选项'})

            # 多选题至少有一个正确选项
            if question_type == Question.Type.MULTI:
                correct_count = sum(1 for opt in options if opt.get('is_correct'))
                if correct_count < 1:
                    raise serializers.ValidationError({'options': '多选题至少有一个正确选项'})

        return attrs

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        tag_ids = validated_data.pop('tag_ids', [])

        # 设置创建者
        validated_data['created_by'] = self.context['request'].user

        question = Question.objects.create(**validated_data)

        # 创建选项
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)

        # 设置标签
        if tag_ids:
            question.tags.set(tag_ids)

        return question


class QuestionUpdateSerializer(serializers.ModelSerializer):
    """
    题目更新序列化器
    """
    options = OptionSerializer(many=True, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Question
        fields = [
            'title', 'type', 'difficulty', 'score',
            'content', 'answer', 'answer_analysis',
            'programming_language', 'time_limit', 'memory_limit', 'test_cases',
            'options', 'tag_ids', 'category', 'is_public'
        ]

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        tag_ids = validated_data.pop('tag_ids', None)

        # 更新基本字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新选项（如果提供）
        if options_data is not None:
            instance.options.all().delete()
            for option_data in options_data:
                Option.objects.create(question=instance, **option_data)

        # 更新标签
        if tag_ids is not None:
            instance.tags.set(tag_ids)

        return instance
