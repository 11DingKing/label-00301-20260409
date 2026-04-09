"""
试卷题目关联模型
"""
from django.db import models

from utils.mixins import OrderMixin


class PaperQuestion(OrderMixin, models.Model):
    """
    试卷-题目关联模型
    记录题目在试卷中的位置和分值
    """
    paper = models.ForeignKey(
        'papers.Paper',
        on_delete=models.CASCADE,
        related_name='paper_questions',
        verbose_name='所属试卷'
    )
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='paper_questions',
        verbose_name='题目'
    )
    section = models.ForeignKey(
        'papers.PaperSection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paper_questions',
        verbose_name='所属大题'
    )

    # 在试卷中的配置
    score = models.DecimalField('分值', max_digits=5, decimal_places=1, default=5)
    question_number = models.PositiveSmallIntegerField('题号', default=1)

    class Meta:
        db_table = 'paper_questions'
        verbose_name = '试卷题目'
        verbose_name_plural = verbose_name
        ordering = ['paper', 'section', 'order', 'question_number']
        unique_together = [['paper', 'question']]

    def __str__(self):
        return f'{self.paper.title} - 第{self.question_number}题'

    def save(self, *args, **kwargs):
        # 如果未设置分值，使用题目的默认分值
        if not self.score:
            self.score = self.question.score
        super().save(*args, **kwargs)
