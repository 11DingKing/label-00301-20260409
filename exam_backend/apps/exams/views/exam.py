"""
考试视图
"""
import random

from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.exams.models import Exam
from apps.exams.serializers import (
    ExamListSerializer,
    ExamDetailSerializer,
    ExamCreateSerializer,
    ExamPaperSerializer,
)
from apps.submissions.models import Submission
from apps.submissions.serializers import SubmissionSerializer
from apps.papers.serializers import PaperExamSerializer
from utils.exceptions import (
    ExamNotStartedException,
    ExamEndedException,
    AlreadySubmittedException,
    InvalidOperationException,
)
from utils.mixins import MultiSerializerMixin, MultiPermissionMixin
from utils.permissions import IsTeacherOrAdmin, IsStudent


class ExamViewSet(MultiSerializerMixin, MultiPermissionMixin, viewsets.ModelViewSet):
    """
    考试管理视图集
    """
    queryset = Exam.objects.filter(is_deleted=False).select_related('paper', 'created_by')
    serializer_class = ExamDetailSerializer  # 默认序列化器
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'type', 'is_public']
    search_fields = ['title', 'description']
    ordering_fields = ['start_time', 'end_time', 'created_at']
    ordering = ['-start_time']

    serializer_classes = {
        'list': ExamListSerializer,
        'retrieve': ExamDetailSerializer,
        'create': ExamCreateSerializer,
        'update': ExamCreateSerializer,
        'default': ExamDetailSerializer,
    }

    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsTeacherOrAdmin],
        'update': [IsTeacherOrAdmin],
        'partial_update': [IsTeacherOrAdmin],
        'destroy': [IsTeacherOrAdmin],
        'start': [IsAuthenticated],
        'my_record': [IsAuthenticated],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 学生只能看公开考试或被允许参加的考试
        if user.role == 'student':
            from django.db.models import Q
            queryset = queryset.filter(
                Q(is_public=True) | Q(allowed_users=user)
            ).distinct()

        return queryset

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        开始考试
        POST /api/v1/exams/{id}/start/
        """
        exam = self.get_object()
        user = request.user

        # 检查考试状态
        if not exam.is_started:
            raise ExamNotStartedException()

        if exam.is_ended:
            raise ExamEndedException()

        # 检查尝试次数
        attempt_count = Submission.objects.filter(exam=exam, user=user).count()
        if attempt_count >= exam.max_attempts:
            raise InvalidOperationException('已达到最大尝试次数')

        # 检查是否有进行中的记录
        ongoing_record = Submission.objects.filter(
            exam=exam,
            user=user,
            status=Submission.Status.IN_PROGRESS
        ).first()

        if ongoing_record:
            # 返回进行中的记录
            serializer = ExamPaperSerializer(ongoing_record)
            return Response({
                'success': True,
                'message': '继续考试',
                'data': {
                    'record': serializer.data,
                    'paper': PaperExamSerializer(exam.paper).data
                }
            })

        # 创建新的考试记录
        with transaction.atomic():
            # 生成题目顺序
            question_order = list(exam.paper.paper_questions.values_list('id', flat=True))
            if exam.paper.is_random_question:
                random.shuffle(question_order)

            record = Submission.objects.create(
                exam=exam,
                user=user,
                status=Submission.Status.IN_PROGRESS,
                attempt=attempt_count + 1,
                start_time=timezone.now(),
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                question_order=question_order,
            )

        serializer = ExamPaperSerializer(record)
        return Response({
            'success': True,
            'message': '考试开始',
            'data': {
                'record': serializer.data,
                'paper': PaperExamSerializer(exam.paper).data
            }
        })

    @action(detail=True, methods=['get'])
    def my_record(self, request, pk=None):
        """
        获取当前用户的考试记录
        GET /api/v1/exams/{id}/my_record/
        """
        exam = self.get_object()
        records = Submission.objects.filter(exam=exam, user=request.user)
        serializer = SubmissionSerializer(records, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['get'], permission_classes=[IsTeacherOrAdmin])
    def records(self, request, pk=None):
        """
        获取考试所有记录（教师/管理员）
        GET /api/v1/exams/{id}/records/
        """
        exam = self.get_object()
        records = Submission.objects.filter(exam=exam).select_related('user')
        serializer = SubmissionSerializer(records, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def publish(self, request, pk=None):
        """
        发布考试
        POST /api/v1/exams/{id}/publish/
        """
        exam = self.get_object()

        if exam.status == Exam.Status.DRAFT:
            exam.status = Exam.Status.NOT_STARTED
            exam.save(update_fields=['status'])

        return Response({
            'success': True,
            'message': '考试已发布'
        })

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        获取可参加的考试列表
        GET /api/v1/exams/available/
        """
        now = timezone.now()
        queryset = self.get_queryset().filter(
            status__in=[Exam.Status.NOT_STARTED, Exam.Status.IN_PROGRESS],
            end_time__gt=now
        )
        serializer = ExamListSerializer(queryset, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    提交记录视图集
    """
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['teacher', 'admin']:
            return Submission.objects.all()
        return Submission.objects.filter(user=user)
