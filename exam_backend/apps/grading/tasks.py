"""
阅卷相关 Celery 任务
"""
from celery import shared_task


@shared_task
def auto_grade_submission(submission_id):
    """
    自动批改客观题
    """
    from apps.submissions.models import Answer, Submission
    from django.db.models import Sum

    try:
        submission = Submission.objects.get(id=submission_id)

        # 批改所有客观题
        objective_score = 0
        for answer in submission.answers.filter(
            paper_question__question__type__in=['single', 'multi', 'judge']
        ):
            if answer.auto_grade():
                objective_score += answer.score or 0

        submission.objective_score = objective_score
        submission.save(update_fields=['objective_score'])

        # 检查是否需要人工阅卷
        has_subjective = submission.answers.filter(
            paper_question__question__type__in=['short', 'programming', 'blank']
        ).exists()

        if not has_subjective:
            # 全是客观题，直接完成
            submission.score = objective_score
            submission.status = Submission.Status.FINISHED
            submission.save(update_fields=['score', 'status'])

    except Submission.DoesNotExist:
        pass


@shared_task
def batch_auto_grade_exam(exam_id):
    """
    批量自动批改考试的所有客观题
    """
    from apps.exams.models import Exam
    from apps.submissions.models import Submission

    try:
        exam = Exam.objects.get(id=exam_id)

        for submission in exam.submissions.filter(
            status__in=[Submission.Status.SUBMITTED, Submission.Status.GRADING]
        ):
            auto_grade_submission.delay(submission.id)

    except Exam.DoesNotExist:
        pass


@shared_task
def notify_grading_complete(submission_id):
    """
    通知用户阅卷完成
    """
    from apps.submissions.models import Submission

    try:
        submission = Submission.objects.get(id=submission_id)

        if submission.status == Submission.Status.FINISHED:
            # TODO: 发送通知（邮件、站内信等）
            # send_notification(
            #     submission.user,
            #     f'您的考试 {submission.exam.title} 已批改完成，得分：{submission.score}'
            # )
            pass

    except Submission.DoesNotExist:
        pass
