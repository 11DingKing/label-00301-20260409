"""
试卷视图
"""
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.papers.models import Paper, PaperSection, PaperQuestion
from apps.papers.serializers import (
    PaperListSerializer,
    PaperDetailSerializer,
    PaperCreateSerializer,
    PaperSectionSerializer,
    PaperQuestionSerializer,
    PaperQuestionBatchSerializer,
)
from apps.questions.models import Question
from utils.mixins import MultiSerializerMixin, MultiPermissionMixin
from utils.permissions import IsTeacherOrAdmin


class PaperViewSet(MultiSerializerMixin, MultiPermissionMixin, viewsets.ModelViewSet):
    """
    试卷管理视图集
    """
    queryset = Paper.objects.filter(is_deleted=False).select_related(
        'created_by', 'category'
    ).prefetch_related('sections', 'paper_questions__question')
    serializer_class = PaperDetailSerializer  # 默认序列化器

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'total_score', 'time_limit']
    ordering = ['-created_at']

    serializer_classes = {
        'list': PaperListSerializer,
        'retrieve': PaperDetailSerializer,
        'create': PaperCreateSerializer,
        'update': PaperCreateSerializer,
        'default': PaperDetailSerializer,
    }

    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsTeacherOrAdmin],
        'update': [IsTeacherOrAdmin],
        'partial_update': [IsTeacherOrAdmin],
        'destroy': [IsTeacherOrAdmin],
    }

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def add_questions(self, request, pk=None):
        """
        批量添加题目到试卷
        POST /api/v1/papers/{id}/add_questions/
        """
        paper = self.get_object()
        serializer = PaperQuestionBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_ids = serializer.validated_data['question_ids']
        section_id = serializer.validated_data.get('section_id')
        default_score = serializer.validated_data.get('score')

        questions = Question.objects.filter(id__in=question_ids, is_deleted=False)
        existing_ids = set(paper.paper_questions.values_list('question_id', flat=True))

        added = []
        with transaction.atomic():
            current_number = paper.paper_questions.count() + 1
            for question in questions:
                if question.id not in existing_ids:
                    pq = PaperQuestion.objects.create(
                        paper=paper,
                        question=question,
                        section_id=section_id,
                        score=default_score or question.score,
                        question_number=current_number,
                        order=current_number
                    )
                    added.append(pq.id)
                    current_number += 1

            # 更新总分
            paper.calculate_total_score()

        return Response({
            'success': True,
            'message': f'成功添加 {len(added)} 道题目',
            'data': {'added_count': len(added)}
        })

    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def remove_questions(self, request, pk=None):
        """
        从试卷移除题目
        POST /api/v1/papers/{id}/remove_questions/
        """
        paper = self.get_object()
        question_ids = request.data.get('question_ids', [])

        deleted_count = paper.paper_questions.filter(question_id__in=question_ids).delete()[0]
        paper.calculate_total_score()

        return Response({
            'success': True,
            'message': f'成功移除 {deleted_count} 道题目',
            'data': {'removed_count': deleted_count}
        })

    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def publish(self, request, pk=None):
        """
        发布试卷
        POST /api/v1/papers/{id}/publish/
        """
        paper = self.get_object()

        if paper.paper_questions.count() == 0:
            return Response({
                'success': False,
                'message': '试卷中没有题目，无法发布'
            }, status=status.HTTP_400_BAD_REQUEST)

        paper.status = Paper.Status.PUBLISHED
        paper.save(update_fields=['status'])

        return Response({
            'success': True,
            'message': '试卷发布成功'
        })

    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def duplicate(self, request, pk=None):
        """
        复制试卷
        POST /api/v1/papers/{id}/duplicate/
        """
        paper = self.get_object()

        with transaction.atomic():
            # 复制试卷
            new_paper = Paper.objects.create(
                title=f'{paper.title} (副本)',
                description=paper.description,
                total_score=paper.total_score,
                pass_score=paper.pass_score,
                time_limit=paper.time_limit,
                status=Paper.Status.DRAFT,
                is_random_question=paper.is_random_question,
                is_random_option=paper.is_random_option,
                show_answer_after_submit=paper.show_answer_after_submit,
                allow_review=paper.allow_review,
                category=paper.category,
                created_by=request.user,
            )

            # 复制大题
            section_map = {}
            for section in paper.sections.all():
                new_section = PaperSection.objects.create(
                    paper=new_paper,
                    title=section.title,
                    description=section.description,
                    question_type=section.question_type,
                    order=section.order,
                )
                section_map[section.id] = new_section

            # 复制题目关联
            for pq in paper.paper_questions.all():
                PaperQuestion.objects.create(
                    paper=new_paper,
                    question=pq.question,
                    section=section_map.get(pq.section_id) if pq.section_id else None,
                    score=pq.score,
                    question_number=pq.question_number,
                    order=pq.order,
                )

        serializer = PaperDetailSerializer(new_paper)
        return Response({
            'success': True,
            'message': '试卷复制成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class PaperSectionViewSet(viewsets.ModelViewSet):
    """
    试卷大题视图集
    """
    serializer_class = PaperSectionSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        return PaperSection.objects.filter(paper_id=self.kwargs['paper_pk'])

    def perform_create(self, serializer):
        serializer.save(paper_id=self.kwargs['paper_pk'])
