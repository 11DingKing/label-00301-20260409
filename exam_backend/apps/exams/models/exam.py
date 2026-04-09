"""
考试模型
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

from utils.mixins import TimeStampMixin, SoftDeleteMixin, CreatedByMixin


class Exam(TimeStampMixin, SoftDeleteMixin, CreatedByMixin, models.Model):
    """
    考试模型
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        NOT_STARTED = 'not_started', '未开始'
        IN_PROGRESS = 'in_progress', '进行中'
        ENDED = 'ended', '已结束'
        GRADING = 'grading', '阅卷中'
        FINISHED = 'finished', '已完成'

    class Type(models.TextChoices):
        EXAM = 'exam', '正式考试'
        PRACTICE = 'practice', '练习模式'
        MOCK = 'mock', '模拟考试'

    # 基本信息
    title = models.CharField('考试名称', max_length=200)
    description = models.TextField('考试说明', blank=True)

    # 关联试卷
    paper = models.ForeignKey(
        'papers.Paper',
        on_delete=models.PROTECT,
        related_name='exams',
        verbose_name='关联试卷'
    )

    # 考试类型和状态
    type = models.CharField(
        '考试类型',
        max_length=20,
        choices=Type.choices,
        default=Type.EXAM
    )
    status = models.CharField(
        '状态',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    # 时间设置
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    is_time_limited = models.BooleanField('是否限时', default=True, help_text='是否启用考试时间限制')
    duration = models.PositiveIntegerField('考试时长(分钟)', help_text='覆盖试卷时长', null=True, blank=True)

    # 考试规则
    max_attempts = models.PositiveSmallIntegerField('最大尝试次数', default=1)
    allow_late_submit = models.BooleanField('允许迟交', default=False)
    late_submit_minutes = models.PositiveIntegerField('迟交时限(分钟)', default=0)

    # 防作弊
    anti_cheat_enabled = models.BooleanField('启用防作弊', default=False)
    fullscreen_required = models.BooleanField('强制全屏', default=False)
    switch_limit = models.PositiveSmallIntegerField('切屏次数限制', default=0)

    # 成绩发布
    auto_publish_score = models.BooleanField('自动发布成绩', default=True)
    score_publish_time = models.DateTimeField('成绩发布时间', null=True, blank=True)

    # 考试范围
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='allowed_exams',
        verbose_name='允许参加的用户'
    )
    is_public = models.BooleanField('是否公开', default=False, help_text='公开考试所有人可参加')

    class Meta:
        db_table = 'exams'
        verbose_name = '考试'
        verbose_name_plural = verbose_name
        ordering = ['-start_time']

    def __str__(self):
        return self.title

    @property
    def actual_duration(self):
        """实际考试时长，如果不限时则返回 None"""
        if not self.is_time_limited:
            return None
        return self.duration or self.paper.time_limit

    @property
    def is_started(self):
        """是否已开始"""
        return timezone.now() >= self.start_time

    @property
    def is_ended(self):
        """是否已结束"""
        return timezone.now() > self.end_time

    @property
    def is_ongoing(self):
        """是否正在进行"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def participant_count(self):
        """参与人数"""
        return self.submissions.count()

    @property
    def submitted_count(self):
        """已提交人数"""
        return self.submissions.filter(status='submitted').count()

    def update_status(self):
        """根据时间更新状态"""
        now = timezone.now()
        if self.status == Exam.Status.DRAFT:
            return

        if now < self.start_time:
            new_status = Exam.Status.NOT_STARTED
        elif now <= self.end_time:
            new_status = Exam.Status.IN_PROGRESS
        else:
            new_status = Exam.Status.ENDED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])
