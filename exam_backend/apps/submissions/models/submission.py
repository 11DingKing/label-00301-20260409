"""
提交记录模型
"""
from django.conf import settings
from django.db import models

from utils.mixins import TimeStampMixin


class Submission(TimeStampMixin, models.Model):
    """
    提交记录模型
    记录用户参加考试的状态
    """

    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', '未开始'
        IN_PROGRESS = 'in_progress', '进行中'
        SUBMITTED = 'submitted', '已提交'
        TIMEOUT = 'timeout', '超时'
        GRADING = 'grading', '阅卷中'
        FINISHED = 'finished', '已完成'

    exam = models.ForeignKey(
        'exams.Exam',
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='考试'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='用户'
    )

    # 状态
    status = models.CharField(
        '状态',
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_STARTED
    )
    attempt = models.PositiveSmallIntegerField('尝试次数', default=1)

    # 时间记录
    start_time = models.DateTimeField('开始答题时间', null=True, blank=True)
    submit_time = models.DateTimeField('提交时间', null=True, blank=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)

    # 成绩
    score = models.DecimalField('得分', max_digits=6, decimal_places=1, null=True, blank=True)
    objective_score = models.DecimalField('客观题得分', max_digits=6, decimal_places=1, null=True, blank=True)
    subjective_score = models.DecimalField('主观题得分', max_digits=6, decimal_places=1, null=True, blank=True)

    # 防作弊记录
    switch_count = models.PositiveSmallIntegerField('切屏次数', default=0)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('浏览器信息', blank=True)

    # 题目顺序（如果随机）
    question_order = models.JSONField('题目顺序', default=list, blank=True)

    class Meta:
        db_table = 'submissions'
        verbose_name = '提交记录'
        verbose_name_plural = verbose_name
        unique_together = [['exam', 'user', 'attempt']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.exam.title}'

    @property
    def is_passed(self):
        """是否及格"""
        if self.score is None:
            return None
        return self.score >= self.exam.paper.pass_score

    @property
    def duration_seconds(self):
        """答题时长（秒）"""
        if self.start_time and (self.submit_time or self.end_time):
            end = self.submit_time or self.end_time
            return (end - self.start_time).total_seconds()
        return None

    @property
    def remaining_time(self):
        """剩余时间（秒）"""
        from django.utils import timezone

        if not self.start_time or self.status != self.Status.IN_PROGRESS:
            return None

        duration_seconds = self.exam.actual_duration * 60
        elapsed = (timezone.now() - self.start_time).total_seconds()
        remaining = duration_seconds - elapsed

        return max(0, int(remaining))
