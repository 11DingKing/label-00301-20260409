"""
答题记录查询视图
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.submissions.models import Answer, Submission
from apps.submissions.serializers import (
    AnswerDetailSerializer,
    AnswerResultSerializer,
    SubmissionSerializer,
)
from utils.exceptions import (
    InvalidOperationException,
    ResourceNotFoundException,
)


class AnswerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    答题记录视图集
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return Answer.objects.filter(
            submission__user=user
        ).select_related(
            'submission', 'paper_question', 'paper_question__question'
        )

    @action(detail=False, methods=['get'])
    def by_submission(self, request):
        """
        获取指定提交记录的所有答题
        GET /api/submissions/answers/by_submission/?submission_id=1
        """
        submission_id = request.query_params.get('submission_id')

        try:
            submission = Submission.objects.get(id=submission_id, user=request.user)
        except Submission.DoesNotExist:
            raise ResourceNotFoundException('提交记录不存在')

        answers = Answer.objects.filter(submission=submission).select_related(
            'paper_question', 'paper_question__question'
        )

        serializer = AnswerDetailSerializer(answers, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def result(self, request):
        """
        获取考试结果（考试结束后）
        GET /api/submissions/answers/result/?submission_id=1
        """
        submission_id = request.query_params.get('submission_id')

        try:
            submission = Submission.objects.get(id=submission_id, user=request.user)
        except Submission.DoesNotExist:
            raise ResourceNotFoundException('提交记录不存在')

        # 检查是否可以查看结果
        if submission.status not in [Submission.Status.SUBMITTED, Submission.Status.FINISHED]:
            raise InvalidOperationException('考试尚未提交')

        if not submission.exam.paper.show_answer_after_submit:
            raise InvalidOperationException('该考试不允许查看答案')

        answers = Answer.objects.filter(submission=submission).select_related(
            'paper_question', 'paper_question__question'
        )

        serializer = AnswerResultSerializer(answers, many=True)
        return Response({
            'success': True,
            'data': {
                'submission': {
                    'id': submission.id,
                    'score': submission.score,
                    'objective_score': submission.objective_score,
                    'subjective_score': submission.subjective_score,
                    'total_score': submission.exam.paper.total_score,
                    'pass_score': submission.exam.paper.pass_score,
                    'is_passed': submission.is_passed,
                },
                'answers': serializer.data
            }
        })
