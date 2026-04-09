"""
试卷大题模型
"""
from django.db import models

from utils.mixins import OrderMixin


class PaperSection(OrderMixin, models.Model):
    """
    试卷大题模型
    用于组织试卷结构，如：一、选择题（每题2分）
    """
    paper = models.ForeignKey(
        'papers.Paper',
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='所属试卷'
    )
    title = models.CharField('大题标题', max_length=200, help_text='如：一、选择题')
    description = models.TextField('说明', blank=True, help_text='如：每题2分，共20分')

    # 题型限制（可选）
    question_type = models.CharField(
        '题目类型',
        max_length=20,
        blank=True,
        help_text='限制此大题只能添加特定类型的题目'
    )

    class Meta:
        db_table = 'paper_sections'
        verbose_name = '试卷大题'
        verbose_name_plural = verbose_name
        ordering = ['paper', 'order']

    def __str__(self):
        return f'{self.paper.title} - {self.title}'

    @property
    def question_count(self):
        """大题中的题目数量"""
        return self.paper_questions.count()

    @property
    def section_score(self):
        """大题总分"""
        return self.paper_questions.aggregate(
            total=models.Sum('score')
        )['total'] or 0
