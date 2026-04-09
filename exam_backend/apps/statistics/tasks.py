"""
统计相关 Celery 任务
"""
from celery import shared_task


@shared_task
def update_statistics():
    """
    定时更新统计数据
    """
    from apps.exams.models import Exam
    from apps.statistics.models import ExamStatistics, UserStatistics
    from apps.submissions.models import Submission
    from django.db.models import Avg, Count, Max, Min, Sum

    # 更新考试统计
    for exam in Exam.objects.filter(is_deleted=False):
        records = Submission.objects.filter(exam=exam)
        finished_records = records.filter(status=Submission.Status.FINISHED)

        stats, created = ExamStatistics.objects.get_or_create(exam=exam)

        stats.participant_count = records.count()
        stats.submitted_count = records.filter(status__in=[
            Submission.Status.SUBMITTED,
            Submission.Status.GRADING,
            Submission.Status.FINISHED
        ]).count()
        stats.graded_count = finished_records.count()

        if finished_records.exists():
            score_data = finished_records.aggregate(
                avg=Avg('score'),
                max=Max('score'),
                min=Min('score')
            )
            stats.average_score = score_data['avg']
            stats.highest_score = score_data['max']
            stats.lowest_score = score_data['min']

            pass_count = finished_records.filter(score__gte=exam.paper.pass_score).count()
            stats.pass_rate = round(pass_count / finished_records.count() * 100, 2)

        stats.save()


@shared_task
def update_user_statistics(user_id):
    """
    更新单个用户的统计数据
    """
    from apps.accounts.models import User
    from apps.statistics.models import UserStatistics
    from apps.submissions.models import Answer, Submission
    from django.db.models import Sum, Avg

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    stats, created = UserStatistics.objects.get_or_create(user=user)

    records = Submission.objects.filter(user=user, status=Submission.Status.FINISHED)

    stats.exam_count = records.count()
    stats.passed_count = sum(1 for r in records if r.is_passed)

    if records.exists():
        score_data = records.aggregate(total=Sum('score'), avg=Avg('score'))
        stats.total_score = score_data['total'] or 0
        stats.average_score = score_data['avg']

    answers = Answer.objects.filter(submission__user=user, status=Answer.Status.GRADED)
    stats.question_count = answers.count()
    stats.correct_count = answers.filter(is_correct=True).count()

    if stats.question_count > 0:
        stats.accuracy_rate = round(stats.correct_count / stats.question_count * 100, 2)

    stats.save()


@shared_task
def generate_exam_report(exam_id):
    """
    生成考试报告
    """
    # TODO: 生成 PDF 报告
    pass
