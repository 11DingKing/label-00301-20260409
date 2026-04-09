"""
标签序列化器
"""
from rest_framework import serializers

from apps.tags.models import Tag, Category


class TagSerializer(serializers.ModelSerializer):
    """
    标签序列化器
    """
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'description', 'question_count', 'is_active']


class TagCreateSerializer(serializers.ModelSerializer):
    """
    标签创建序列化器
    """

    class Meta:
        model = Tag
        fields = ['name', 'color', 'description', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    """
    分类序列化器
    """
    children = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'parent', 'order', 'children', 'question_count', 'is_active']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data

    def get_question_count(self, obj):
        return obj.questions.count()


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    分类创建序列化器
    """

    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'parent', 'order', 'is_active']


class CategoryTreeSerializer(serializers.ModelSerializer):
    """
    分类树形序列化器
    """
    children = serializers.SerializerMethodField()
    full_path = serializers.CharField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'full_path', 'children']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('order')
        return CategoryTreeSerializer(children, many=True).data
