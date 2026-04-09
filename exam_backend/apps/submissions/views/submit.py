"""
提交相关视图
"""
from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.exams.models import Exam
from apps.papers.models import PaperQuestion
from apps.submissions.models import Answer, Submission
from apps.submissions.serializers import (
    AnswerSerializer,
    AnswerSubmitSerializer,
    BatchAnswerSubmitSerializer,
    ExamSubmitSerializer,
)
from utils.exceptions import (
    ExamEndedException,
    AlreadySubmittedException,
    InvalidOperationException,
    ResourceNotFoundException,
)


class SubmitViewSet(viewsets.ViewSet):
    """
    提交视图集
    处理考试提交相关操作
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """
        提交考试
        POST /api/submissions/{exam_id}/submit/
        """
        exam_id = pk

        # 验证考试存在
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            raise ResourceNotFoundException('考试不存在')

        # 获取用户的提交记录
        try:
            submission = Submission.objects.get(
                exam=exam,
                user=request.user,
                status=Submission.Status.IN_PROGRESS
            )
        except Submission.DoesNotExist:
            raise ResourceNotFoundException('未找到进行中的提交记录')

        serializer = ExamSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers_data = serializer.validated_data.get('answers', [])

        if submission.status == Submission.Status.SUBMITTED:
            raise AlreadySubmittedException()

        if submission.status != Submission.Status.IN_PROGRESS:
            raise InvalidOperationException('考试状态异常')

        now = timezone.now()

        with transaction.atomic():
            # 保存最后提交的答案
            if answers_data:
                for answer_data in answers_data:
                    paper_question_id = answer_data['paper_question_id']
                    answer_content = answer_data.get('answer_content', '')

                    try:
                        paper_question = PaperQuestion.objects.get(
                            id=paper_question_id,
                            paper=submission.exam.paper
                        )
                        Answer.objects.update_or_create(
                            submission=submission,
                            paper_question=paper_question,
                            defaults={
                                'answer_content': answer_content,
                                'status': Answer.Status.ANSWERED if answer_content else Answer.Status.NOT_ANSWERED,
                                'last_answer_time': now,
                            }
                        )
                    except PaperQuestion.DoesNotExist:
                        continue

            # 更新提交记录状态
            submission.status = Submission.Status.SUBMITTED
            submission.submit_time = now
            submission.save(update_fields=['status', 'submit_time'])

            # 自动批改客观题
            objective_score = 0
            for answer in submission.answers.all():
                if answer.question.is_objective:
                    answer.auto_grade()
                    if answer.score:
                        objective_score += answer.score

            submission.objective_score = objective_score
            submission.save(update_fields=['objective_score'])

            # 检查是否需要人工阅卷
            has_subjective = submission.answers.filter(
                paper_question__question__type__in=['short', 'programming', 'blank']
            ).exists()

            if has_subjective:
                submission.status = Submission.Status.GRADING
            else:
                # 全是客观题，直接计算总分
                submission.score = objective_score
                submission.status = Submission.Status.FINISHED

            submission.save(update_fields=['status', 'score'])

        return Response({
            'success': True,
            'message': '考试已提交',
            'data': {
                'submission_id': submission.id,
                'status': submission.status,
                'score': submission.score,
                'objective_score': submission.objective_score,
            }
        })

    @action(detail=True, methods=['post'], url_path='save_answer')
    def save_answer(self, request, pk=None):
        """
        保存单个答案（自动保存）
        POST /api/submissions/{exam_id}/save_answer/
        """
        exam_id = pk

        # 验证考试存在
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            raise ResourceNotFoundException('考试不存在')

        serializer = AnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        paper_question_id = serializer.validated_data['paper_question_id']
        answer_content = serializer.validated_data.get('answer_content', '')
        answer_files = serializer.validated_data.get('answer_files', [])
        is_marked = serializer.validated_data.get('is_marked', False)

        # 获取用户的提交记录
        try:
            submission = Submission.objects.get(
                exam=exam,
                user=request.user,
                status=Submission.Status.IN_PROGRESS
            )
        except Submission.DoesNotExist:
            raise ResourceNotFoundException('未找到进行中的提交记录')

        # 检查考试状态
        if submission.status != Submission.Status.IN_PROGRESS:
            raise InvalidOperationException('考试已结束，无法保存答案')

        # 检查剩余时间
        if submission.remaining_time is not None and submission.remaining_time <= 0:
            raise ExamEndedException()

        # 验证题目
        try:
            paper_question = PaperQuestion.objects.get(
                id=paper_question_id,
                paper=submission.exam.paper
            )
        except PaperQuestion.DoesNotExist:
            raise ResourceNotFoundException('题目不存在')

        # 保存或更新答案
        now = timezone.now()
        answer, created = Answer.objects.get_or_create(
            submission=submission,
            paper_question=paper_question,
            defaults={
                'answer_content': answer_content,
                'answer_files': answer_files,
                'is_marked': is_marked,
                'status': Answer.Status.ANSWERED if answer_content else Answer.Status.NOT_ANSWERED,
                'first_answer_time': now,
                'last_answer_time': now,
            }
        )

        if not created:
            # 计算作答时长
            if answer.first_answer_time:
                answer.answer_duration += int((now - answer.last_answer_time).total_seconds())

            answer.answer_content = answer_content
            answer.answer_files = answer_files
            answer.is_marked = is_marked
            answer.status = Answer.Status.ANSWERED if answer_content else Answer.Status.NOT_ANSWERED
            answer.last_answer_time = now
            answer.save()

        return Response({
            'success': True,
            'message': '答案已保存',
            'data': AnswerSerializer(answer).data
        })

    @action(detail=True, methods=['post'], url_path='batch_save')
    def batch_save(self, request, pk=None):
        """
        批量保存答案
        POST /api/submissions/{exam_id}/batch_save/
        """
        exam_id = pk

        # 验证考试存在
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            raise ResourceNotFoundException('考试不存在')

        serializer = BatchAnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取用户的提交记录
        try:
            submission = Submission.objects.get(
                exam=exam,
                user=request.user,
                status=Submission.Status.IN_PROGRESS
            )
        except Submission.DoesNotExist:
            raise ResourceNotFoundException('未找到进行中的提交记录')

        if submission.status != Submission.Status.IN_PROGRESS:
            raise InvalidOperationException('考试已结束')

        now = timezone.now()
        saved_count = 0

        with transaction.atomic():
            for answer_data in serializer.validated_data['answers']:
                paper_question_id = answer_data['paper_question_id']
                answer_content = answer_data.get('answer_content', '')
                answer_files = answer_data.get('answer_files', [])
                is_marked = answer_data.get('is_marked', False)

                try:
                    paper_question = PaperQuestion.objects.get(
                        id=paper_question_id,
                        paper=submission.exam.paper
                    )
                except PaperQuestion.DoesNotExist:
                    continue

                answer, created = Answer.objects.update_or_create(
                    submission=submission,
                    paper_question=paper_question,
                    defaults={
                        'answer_content': answer_content,
                        'answer_files': answer_files,
                        'is_marked': is_marked,
                        'status': Answer.Status.ANSWERED if answer_content else Answer.Status.NOT_ANSWERED,
                        'last_answer_time': now,
                    }
                )
                if created:
                    answer.first_answer_time = now
                    answer.save(update_fields=['first_answer_time'])

                saved_count += 1

        return Response({
            'success': True,
            'message': f'已保存 {saved_count} 个答案'
        })
