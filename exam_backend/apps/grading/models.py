"""
阅卷相关模型
"""
from django.conf import settings
from django.db import models

from utils.mixins import TimeStampMixin


class GradingTask(TimeStampMixin, models.Model):
    """
    阅卷任务模型
    """

    class Status(models.TextChoices):
        PENDING = 'pending', '待分配'
        IN_PROGRESS = 'in_progress', '进行中'
        COMPLETED = 'completed', '已完成'
        REVIEWED = 'reviewed', '已复核'

    exam = models.ForeignKey(
        'exams.Exam',
        on_delete=models.CASCADE,
        related_name='grading_tasks',
        verbose_name='考试'
    )
    grader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grading_tasks',
        verbose_name='阅卷人'
    )

    # 任务范围
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='grading_tasks',
        verbose_name='指定题目',
        help_text='如果指定，只批改该题目'
    )

    status = models.CharField(
        '状态',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # 进度
    total_count = models.PositiveIntegerField('总数', default=0)
    graded_count = models.PositiveIntegerField('已批改数', default=0)

    # 时间
    assigned_at = models.DateTimeField('分配时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        db_table = 'grading_tasks'
        verbose_name = '阅卷任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.exam.title} - {self.grader.username if self.grader else "未分配"}'

    @property
    def progress(self):
        """批改进度"""
        if self.total_count == 0:
            return 0
        return round(self.graded_count / self.total_count * 100, 2)
