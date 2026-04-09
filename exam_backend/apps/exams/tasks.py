"""
考试相关 Celery 任务
"""
from celery import shared_task
from django.utils import timezone


@shared_task
def cleanup_expired_exams():
    """
    清理过期的考试数据
    - 更新过期考试的状态
    - 处理超时未提交的提交记录
    """
    from apps.exams.models import Exam
    from apps.submissions.models import Submission

    now = timezone.now()

    # 更新已结束的考试状态
    Exam.objects.filter(
        end_time__lt=now,
        status__in=[Exam.Status.NOT_STARTED, Exam.Status.IN_PROGRESS]
    ).update(status=Exam.Status.ENDED)

    # 处理超时的提交记录
    timeout_records = Submission.objects.filter(
        status=Submission.Status.IN_PROGRESS
    ).select_related('exam')

    for record in timeout_records:
        # 计算是否超时
        if record.start_time:
            elapsed = (now - record.start_time).total_seconds()
            max_duration = record.exam.actual_duration * 60

            # 加上迟交时限
            if record.exam.allow_late_submit:
                max_duration += record.exam.late_submit_minutes * 60

            if elapsed > max_duration:
                record.status = Submission.Status.TIMEOUT
                record.end_time = now
                record.save(update_fields=['status', 'end_time'])


@shared_task
def auto_submit_exam(submission_id):
    """
    自动提交考试
    用于考试时间到期自动提交
    """
    from apps.submissions.models import Submission

    try:
        submission = Submission.objects.get(id=submission_id)
        if submission.status == Submission.Status.IN_PROGRESS:
            submission.status = Submission.Status.TIMEOUT
            submission.end_time = timezone.now()
            submission.save(update_fields=['status', 'end_time'])

            # 触发自动阅卷
            from apps.grading.tasks import auto_grade_submission
            auto_grade_submission.delay(submission_id)

    except Submission.DoesNotExist:
        pass


@shared_task
def send_exam_reminder(exam_id, minutes_before=30):
    """
    发送考试提醒
    """
    from apps.exams.models import Exam

    try:
        exam = Exam.objects.get(id=exam_id)

        # 获取需要提醒的用户
        if exam.is_public:
            from apps.accounts.models import User
            users = User.objects.filter(is_active=True, role='student')
        else:
            users = exam.allowed_users.filter(is_active=True)

        # TODO: 发送提醒通知（邮件、站内信等）
        for user in users:
            # send_notification(user, f'考试提醒：{exam.title} 将在 {minutes_before} 分钟后开始')
            pass

    except Exam.DoesNotExist:
        pass
