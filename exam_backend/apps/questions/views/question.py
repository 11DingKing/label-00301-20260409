"""
题目视图
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.questions.filters import QuestionFilter
from apps.questions.models import Question
from apps.questions.serializers import (
    QuestionListSerializer,
    QuestionDetailSerializer,
    QuestionCreateSerializer,
    QuestionUpdateSerializer,
)
from utils.mixins import MultiSerializerMixin, MultiPermissionMixin
from utils.permissions import IsTeacherOrAdmin, ReadOnly


class QuestionViewSet(MultiSerializerMixin, MultiPermissionMixin, viewsets.ModelViewSet):
    """
    题目管理视图集
    """
    queryset = Question.objects.filter(is_deleted=False).select_related(
        'created_by', 'category'
    ).prefetch_related('tags', 'options', 'attachments')
    serializer_class = QuestionDetailSerializer  # 默认序列化器

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = QuestionFilter
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'difficulty', 'use_count', 'correct_rate']
    ordering = ['-created_at']

    serializer_classes = {
        'list': QuestionListSerializer,
        'retrieve': QuestionDetailSerializer,
        'create': QuestionCreateSerializer,
        'update': QuestionUpdateSerializer,
        'partial_update': QuestionUpdateSerializer,
        'default': QuestionDetailSerializer,
    }

    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsTeacherOrAdmin],
        'update': [IsTeacherOrAdmin],
        'partial_update': [IsTeacherOrAdmin],
        'destroy': [IsTeacherOrAdmin],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 学生只能看公开题目
        if user.role == 'student':
            queryset = queryset.filter(is_public=True)

        return queryset

    def perform_destroy(self, instance):
        """软删除"""
        instance.soft_delete()

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        题目统计
        GET /api/v1/questions/statistics/
        """
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'by_type': {},
            'by_difficulty': {},
        }

        for type_choice in Question.Type.choices:
            stats['by_type'][type_choice[1]] = queryset.filter(type=type_choice[0]).count()

        for diff_choice in Question.Difficulty.choices:
            stats['by_difficulty'][diff_choice[1]] = queryset.filter(difficulty=diff_choice[0]).count()

        return Response({
            'success': True,
            'data': stats
        })

    @action(detail=False, methods=['get'])
    def random(self, request):
        """
        随机获取题目
        GET /api/v1/questions/random/?count=10&type=single&difficulty=2
        """
        queryset = self.filter_queryset(self.get_queryset())
        count = int(request.query_params.get('count', 10))

        # 随机排序并取指定数量
        questions = queryset.order_by('?')[:count]
        serializer = QuestionListSerializer(questions, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def duplicate(self, request, pk=None):
        """
        复制题目
        POST /api/v1/questions/{id}/duplicate/
        """
        question = self.get_object()

        # 复制题目
        new_question = Question.objects.create(
            title=f'{question.title} (副本)',
            type=question.type,
            difficulty=question.difficulty,
            score=question.score,
            content=question.content,
            answer=question.answer,
            answer_analysis=question.answer_analysis,
            programming_language=question.programming_language,
            time_limit=question.time_limit,
            memory_limit=question.memory_limit,
            test_cases=question.test_cases,
            category=question.category,
            is_public=False,  # 副本默认不公开
            created_by=request.user,
        )

        # 复制选项
        for option in question.options.all():
            option.pk = None
            option.question = new_question
            option.save()

        # 复制标签
        new_question.tags.set(question.tags.all())

        serializer = QuestionDetailSerializer(new_question)
        return Response({
            'success': True,
            'message': '题目复制成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
