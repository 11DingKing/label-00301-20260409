"""
标签视图
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tags.models import Tag, Category
from apps.tags.serializers import (
    TagSerializer,
    TagCreateSerializer,
    CategorySerializer,
    CategoryCreateSerializer,
    CategoryTreeSerializer,
)
from utils.mixins import MultiSerializerMixin, MultiPermissionMixin
from utils.permissions import IsTeacherOrAdmin


class TagViewSet(MultiSerializerMixin, MultiPermissionMixin, viewsets.ModelViewSet):
    """
    标签管理视图集
    """
    queryset = Tag.objects.filter(is_active=True)
    serializer_class = TagSerializer  # 默认序列化器

    serializer_classes = {
        'list': TagSerializer,
        'retrieve': TagSerializer,
        'create': TagCreateSerializer,
        'update': TagCreateSerializer,
        'default': TagSerializer,
    }

    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsTeacherOrAdmin],
        'update': [IsTeacherOrAdmin],
        'partial_update': [IsTeacherOrAdmin],
        'destroy': [IsTeacherOrAdmin],
    }


class CategoryViewSet(MultiSerializerMixin, MultiPermissionMixin, viewsets.ModelViewSet):
    """
    分类管理视图集
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer  # 默认序列化器

    serializer_classes = {
        'list': CategorySerializer,
        'retrieve': CategorySerializer,
        'create': CategoryCreateSerializer,
        'update': CategoryCreateSerializer,
        'tree': CategoryTreeSerializer,
        'default': CategorySerializer,
    }

    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'tree': [IsAuthenticated],
        'create': [IsTeacherOrAdmin],
        'update': [IsTeacherOrAdmin],
        'partial_update': [IsTeacherOrAdmin],
        'destroy': [IsTeacherOrAdmin],
    }

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        获取分类树
        GET /api/v1/tags/categories/tree/
        """
        # 只获取顶级分类
        categories = self.queryset.filter(parent__isnull=True).order_by('order')
        serializer = CategoryTreeSerializer(categories, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })
