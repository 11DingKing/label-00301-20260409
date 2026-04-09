"""
试卷模型
"""
from django.conf import settings
from django.db import models

from utils.mixins import TimeStampMixin, SoftDeleteMixin, CreatedByMixin


class Paper(TimeStampMixin, SoftDeleteMixin, CreatedByMixin, models.Model):
    """
    试卷模型
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PUBLISHED = 'published', '已发布'
        ARCHIVED = 'archived', '已归档'

    # 基本信息
    title = models.CharField('试卷标题', max_length=200)
    description = models.TextField('试卷描述', blank=True)

    # 试卷配置
    total_score = models.DecimalField('总分', max_digits=6, decimal_places=1, default=100)
    pass_score = models.DecimalField('及格分', max_digits=6, decimal_places=1, default=60)
    time_limit = models.PositiveIntegerField('时间限制(分钟)', default=120)

    # 状态
    status = models.CharField(
        '状态',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    # 设置
    is_random_question = models.BooleanField('是否随机题目顺序', default=False)
    is_random_option = models.BooleanField('是否随机选项顺序', default=False)
    show_answer_after_submit = models.BooleanField('提交后显示答案', default=True)
    allow_review = models.BooleanField('允许查看解析', default=True)

    # 分类
    category = models.ForeignKey(
        'tags.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='papers',
        verbose_name='分类'
    )

    class Meta:
        db_table = 'papers'
        verbose_name = '试卷'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        """题目数量"""
        return self.paper_questions.count()

    @property
    def actual_total_score(self):
        """实际总分（根据题目计算）"""
        return self.paper_questions.aggregate(
            total=models.Sum('score')
        )['total'] or 0

    def calculate_total_score(self):
        """计算并更新总分"""
        self.total_score = self.actual_total_score
        self.save(update_fields=['total_score'])
