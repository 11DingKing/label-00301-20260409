"""
阅卷视图
"""
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.exams.models import Exam
from apps.grading.models import GradingTask
from apps.grading.serializers import (
    GradingTaskSerializer,
    GradeAnswerSerializer,
    BatchGradeSerializer,
    AnswerToGradeSerializer,
)
from apps.submissions.models import Answer, Submission
from utils.permissions import IsTeacherOrAdmin


class GradingViewSet(viewsets.ViewSet):
    """
    阅卷视图集
    """
    permission_classes = [IsTeacherOrAdmin]

    @action(detail=False, methods=['get'])
    def tasks(self, request):
        """
        获取阅卷任务列表
        GET /api/v1/grading/tasks/
        """
        tasks = GradingTask.objects.filter(grader=request.user).select_related('exam', 'grader')
        serializer = GradingTaskSerializer(tasks, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def pending_exams(self, request):
        """
        获取待阅卷的考试列表
        GET /api/v1/grading/pending_exams/
        """
        # 获取有待批改主观题的考试
        exams = Exam.objects.filter(
            status__in=[Exam.Status.ENDED, Exam.Status.GRADING],
            is_deleted=False
        ).select_related('paper')

        result = []
        for exam in exams:
            pending_count = Answer.objects.filter(
                submission__exam=exam,
                paper_question__question__type__in=['short', 'programming', 'blank'],
                status__in=[Answer.Status.ANSWERED, Answer.Status.MARKED]
            ).count()

            if pending_count > 0:
                result.append({
                    'exam_id': exam.id,
                    'exam_title': exam.title,
                    'pending_count': pending_count,
                    'total_records': exam.submissions.count(),
                })

        return Response({
            'success': True,
            'data': result
        })

    @action(detail=False, methods=['get'])
    def get_answers_to_grade(self, request):
        """
        获取待批改的答案
        GET /api/v1/grading/get_answers_to_grade/?exam_id=1&question_id=2
        """
        exam_id = request.query_params.get('exam_id')
        question_id = request.query_params.get('question_id')

        queryset = Answer.objects.filter(
            status__in=[Answer.Status.ANSWERED, Answer.Status.MARKED]
        ).select_related(
            'submission', 'submission__user',
            'paper_question', 'paper_question__question'
        )

        if exam_id:
            queryset = queryset.filter(submission__exam_id=exam_id)

        if question_id:
            queryset = queryset.filter(paper_question__question_id=question_id)
        else:
            # 只获取主观题
            queryset = queryset.filter(
                paper_question__question__type__in=['short', 'programming', 'blank']
            )

        serializer = AnswerToGradeSerializer(queryset[:50], many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'total': queryset.count()
        })

    @action(detail=False, methods=['post'])
    def grade_answer(self, request):
        """
        批改单个答案
        POST /api/v1/grading/grade_answer/
        """
        serializer = GradeAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answer_id = serializer.validated_data['answer_id']
        score = serializer.validated_data['score']
        comment = serializer.validated_data.get('comment', '')

        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            return Response({
                'success': False,
                'message': '答案不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 验证分数不超过满分
        if score > answer.max_score:
            return Response({
                'success': False,
                'message': f'分数不能超过满分 {answer.max_score}'
            }, status=status.HTTP_400_BAD_REQUEST)

        answer.score = score
        answer.comment = comment
        answer.status = Answer.Status.GRADED
        answer.graded_by = request.user
        answer.graded_at = timezone.now()
        answer.is_correct = score == answer.max_score
        answer.save()

        # 检查是否所有答案都已批改
        self._check_and_update_submission(answer.submission)

        return Response({
            'success': True,
            'message': '批改成功'
        })

    @action(detail=False, methods=['post'])
    def batch_grade(self, request):
        """
        批量批改
        POST /api/v1/grading/batch_grade/
        """
        serializer = BatchGradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        grades = serializer.validated_data['grades']
        success_count = 0
        submissions_to_check = set()

        with transaction.atomic():
            for grade_data in grades:
                try:
                    answer = Answer.objects.get(id=grade_data['answer_id'])
                    if grade_data['score'] <= answer.max_score:
                        answer.score = grade_data['score']
                        answer.comment = grade_data.get('comment', '')
                        answer.status = Answer.Status.GRADED
                        answer.graded_by = request.user
                        answer.graded_at = timezone.now()
                        answer.is_correct = grade_data['score'] == answer.max_score
                        answer.save()
                        success_count += 1
                        submissions_to_check.add(answer.submission_id)
                except Answer.DoesNotExist:
                    continue

            # 检查并更新提交记录
            for submission_id in submissions_to_check:
                try:
                    submission = Submission.objects.get(id=submission_id)
                    self._check_and_update_submission(submission)
                except Submission.DoesNotExist:
                    pass

        return Response({
            'success': True,
            'message': f'成功批改 {success_count} 个答案'
        })

    def _check_and_update_submission(self, submission):
        """
        检查并更新提交记录状态和分数
        """
        # 检查是否所有答案都已批改
        ungraded = submission.answers.exclude(status=Answer.Status.GRADED).exists()

        if not ungraded:
            # 计算总分
            total_score = submission.answers.aggregate(
                total=Sum('score')
            )['total'] or 0

            subjective_score = submission.answers.filter(
                paper_question__question__type__in=['short', 'programming', 'blank']
            ).aggregate(total=Sum('score'))['total'] or 0

            submission.score = total_score
            submission.subjective_score = subjective_score
            submission.status = Submission.Status.FINISHED
            submission.save(update_fields=['score', 'subjective_score', 'status'])


class GradingTaskViewSet(viewsets.ModelViewSet):
    """
    阅卷任务管理视图集
    """
    queryset = GradingTask.objects.all()
    serializer_class = GradingTaskSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return GradingTask.objects.all()
        return GradingTask.objects.filter(grader=user)
