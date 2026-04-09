"""
统计视图
"""
from collections import defaultdict

from django.db.models import Avg, Count, Max, Min, Sum
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.models import Exam
from apps.questions.models import Question
from apps.statistics.models import ExamStatistics, UserStatistics
from apps.statistics.serializers import (
    ExamStatisticsSerializer,
    UserStatisticsSerializer,
)
from apps.submissions.models import Answer, Submission
from utils.permissions import IsTeacherOrAdmin


class ExamStatisticsView(APIView):
    """
    考试统计视图
    GET /api/statistics/exam/{id}/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        """获取考试统计"""
        exam = get_object_or_404(Exam, id=exam_id)
        stats = self._calculate_exam_statistics(exam)
        return Response({
            'success': True,
            'data': stats
        })

    def _calculate_exam_statistics(self, exam):
        """计算考试统计数据"""
        records = Submission.objects.filter(exam=exam)
        finished_records = records.filter(status=Submission.Status.FINISHED)

        stats = {
            'exam_id': exam.id,
            'exam_title': exam.title,
            'participant_count': records.count(),
            'submitted_count': records.filter(status__in=[
                Submission.Status.SUBMITTED,
                Submission.Status.GRADING,
                Submission.Status.FINISHED
            ]).count(),
            'graded_count': finished_records.count(),
        }

        if finished_records.exists():
            score_stats = finished_records.aggregate(
                avg=Avg('score'),
                max=Max('score'),
                min=Min('score')
            )
            stats['average_score'] = round(float(score_stats['avg'] or 0), 2)
            stats['highest_score'] = float(score_stats['max'] or 0)
            stats['lowest_score'] = float(score_stats['min'] or 0)

            # 及格率
            pass_count = finished_records.filter(score__gte=exam.paper.pass_score).count()
            stats['pass_rate'] = round(pass_count / finished_records.count() * 100, 2)

            # 分数分布
            distribution = {'0-59': 0, '60-69': 0, '70-79': 0, '80-89': 0, '90-100': 0}
            for record in finished_records:
                score = float(record.score or 0)
                if score < 60:
                    distribution['0-59'] += 1
                elif score < 70:
                    distribution['60-69'] += 1
                elif score < 80:
                    distribution['70-79'] += 1
                elif score < 90:
                    distribution['80-89'] += 1
                else:
                    distribution['90-100'] += 1
            stats['score_distribution'] = distribution

        return stats


class ExamRankingView(APIView):
    """
    考试排名视图
    GET /api/statistics/exam/{id}/ranking/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        """获取考试排名"""
        get_object_or_404(Exam, id=exam_id)

        records = Submission.objects.filter(
            exam_id=exam_id,
            status=Submission.Status.FINISHED
        ).select_related('user').order_by('-score', 'submit_time')

        ranking = []
        for rank, record in enumerate(records, 1):
            ranking.append({
                'rank': rank,
                'user_id': record.user_id,
                'user_name': record.user.username,
                'score': record.score,
                'duration': record.duration_seconds,
                'submit_time': record.submit_time,
            })

        return Response({
            'success': True,
            'data': ranking
        })


class ExamQuestionAnalysisView(APIView):
    """
    考试题目分析视图
    GET /api/statistics/exam/{id}/question_analysis/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        """获取题目分析"""
        exam = get_object_or_404(Exam, id=exam_id)

        # 分析每道题的作答情况
        analysis = []
        for pq in exam.paper.paper_questions.select_related('question'):
            answers = Answer.objects.filter(
                submission__exam=exam,
                paper_question=pq,
                status=Answer.Status.GRADED
            )

            total = answers.count()
            correct = answers.filter(is_correct=True).count()
            avg_score = answers.aggregate(avg=Avg('score'))['avg'] or 0

            analysis.append({
                'question_id': pq.question.id,
                'question_number': pq.question_number,
                'question_title': pq.question.title[:50],
                'question_type': pq.question.get_type_display(),
                'max_score': float(pq.score),
                'total_count': total,
                'correct_count': correct,
                'correct_rate': round(correct / total * 100, 2) if total > 0 else 0,
                'average_score': round(float(avg_score), 2),
            })

        return Response({
            'success': True,
            'data': analysis
        })


class StatisticsViewSet(viewsets.ViewSet):
    """
    统计视图集（用于用户相关统计）
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_statistics(self, request):
        """
        获取当前用户学习统计
        GET /api/v1/statistics/my_statistics/
        """
        user = request.user
        stats, created = UserStatistics.objects.get_or_create(user=user)

        if created or self._should_update(stats):
            self._calculate_user_statistics(user, stats)

        serializer = UserStatisticsSerializer(stats)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def my_exam_history(self, request):
        """
        获取当前用户考试历史
        GET /api/v1/statistics/my_exam_history/
        """
        records = Submission.objects.filter(
            user=request.user
        ).select_related('exam', 'exam__paper').order_by('-created_at')

        history = []
        for record in records:
            history.append({
                'exam_id': record.exam.id,
                'exam_title': record.exam.title,
                'score': record.score,
                'total_score': record.exam.paper.total_score,
                'pass_score': record.exam.paper.pass_score,
                'is_passed': record.is_passed,
                'status': record.get_status_display(),
                'attempt': record.attempt,
                'submit_time': record.submit_time,
                'duration': record.duration_seconds,
            })

        return Response({
            'success': True,
            'data': history
        })

    @action(detail=False, methods=['get'])
    def my_weak_points(self, request):
        """
        获取薄弱知识点
        GET /api/v1/statistics/my_weak_points/
        """
        user = request.user

        # 统计每个标签的正确率
        tag_stats = defaultdict(lambda: {'correct': 0, 'total': 0})

        answers = Answer.objects.filter(
            submission__user=user,
            status=Answer.Status.GRADED
        ).select_related('paper_question__question')

        for answer in answers:
            question = answer.paper_question.question
            for tag in question.tags.all():
                tag_stats[tag.name]['total'] += 1
                if answer.is_correct:
                    tag_stats[tag.name]['correct'] += 1

        # 计算正确率并排序
        weak_points = []
        for tag_name, stats in tag_stats.items():
            if stats['total'] >= 5:  # 至少5道题才有意义
                rate = stats['correct'] / stats['total'] * 100
                if rate < 60:  # 正确率低于60%认为是薄弱点
                    weak_points.append({
                        'tag': tag_name,
                        'correct_count': stats['correct'],
                        'total_count': stats['total'],
                        'correct_rate': round(rate, 2)
                    })

        weak_points.sort(key=lambda x: x['correct_rate'])

        return Response({
            'success': True,
            'data': weak_points[:10]  # 返回前10个薄弱点
        })

    @action(detail=False, methods=['get'], permission_classes=[IsTeacherOrAdmin])
    def overview(self, request):
        """
        获取系统总览（教师/管理员）
        GET /api/v1/statistics/overview/
        """
        from django.utils import timezone
        from apps.accounts.models import User

        overview = {
            'users': {
                'total': User.objects.count(),
                'students': User.objects.filter(role='student').count(),
                'teachers': User.objects.filter(role='teacher').count(),
            },
            'questions': {
                'total': Question.objects.filter(is_deleted=False).count(),
                'by_type': {}
            },
            'exams': {
                'total': Exam.objects.filter(is_deleted=False).count(),
                'in_progress': Exam.objects.filter(status=Exam.Status.IN_PROGRESS).count(),
            },
            'submissions': {
                'total': Submission.objects.count(),
                'today': Submission.objects.filter(
                    created_at__date=timezone.now().date()
                ).count(),
            }
        }

        for type_choice in Question.Type.choices:
            overview['questions']['by_type'][type_choice[1]] = Question.objects.filter(
                type=type_choice[0], is_deleted=False
            ).count()

        return Response({
            'success': True,
            'data': overview
        })

    def _calculate_exam_statistics(self, exam):
        """计算考试统计数据"""
        records = Submission.objects.filter(exam=exam)
        finished_records = records.filter(status=Submission.Status.FINISHED)

        stats = {
            'exam_id': exam.id,
            'exam_title': exam.title,
            'participant_count': records.count(),
            'submitted_count': records.filter(status__in=[
                Submission.Status.SUBMITTED,
                Submission.Status.GRADING,
                Submission.Status.FINISHED
            ]).count(),
            'graded_count': finished_records.count(),
        }

        if finished_records.exists():
            score_stats = finished_records.aggregate(
                avg=Avg('score'),
                max=Max('score'),
                min=Min('score')
            )
            stats['average_score'] = round(float(score_stats['avg'] or 0), 2)
            stats['highest_score'] = float(score_stats['max'] or 0)
            stats['lowest_score'] = float(score_stats['min'] or 0)

            # 及格率
            pass_count = finished_records.filter(score__gte=exam.paper.pass_score).count()
            stats['pass_rate'] = round(pass_count / finished_records.count() * 100, 2)

            # 分数分布
            distribution = {'0-59': 0, '60-69': 0, '70-79': 0, '80-89': 0, '90-100': 0}
            for record in finished_records:
                score = float(record.score or 0)
                if score < 60:
                    distribution['0-59'] += 1
                elif score < 70:
                    distribution['60-69'] += 1
                elif score < 80:
                    distribution['70-79'] += 1
                elif score < 90:
                    distribution['80-89'] += 1
                else:
                    distribution['90-100'] += 1
            stats['score_distribution'] = distribution

        return stats

    def _calculate_user_statistics(self, user, stats):
        """计算用户统计数据"""
        records = Submission.objects.filter(user=user, status=Submission.Status.FINISHED)

        stats.exam_count = records.count()
        stats.passed_count = sum(1 for r in records if r.is_passed)

        if records.exists():
            score_data = records.aggregate(total=Sum('score'), avg=Avg('score'))
            stats.total_score = score_data['total'] or 0
            stats.average_score = round(float(score_data['avg'] or 0), 2)

        # 答题统计
        answers = Answer.objects.filter(submission__user=user, status=Answer.Status.GRADED)
        stats.question_count = answers.count()
        stats.correct_count = answers.filter(is_correct=True).count()

        if stats.question_count > 0:
            stats.accuracy_rate = round(stats.correct_count / stats.question_count * 100, 2)

        # 学习时长
        stats.total_duration = sum(
            (r.duration_seconds or 0) for r in records
        )

        stats.save()

    def _should_update(self, stats):
        """判断是否需要更新统计"""
        from django.utils import timezone
        if not stats.updated_at:
            return True
        # 如果超过1小时没更新，则更新
        return (timezone.now() - stats.updated_at).seconds > 3600
