"""
选项模型（用于选择题）
"""
from django.db import models

from utils.mixins import OrderMixin


class Option(OrderMixin, models.Model):
    """
    选择题选项模型
    """
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='所属题目'
    )
    label = models.CharField('选项标识', max_length=10, default='A', help_text='如 A, B, C, D')
    content = models.TextField('选项内容')
    is_correct = models.BooleanField('是否正确', default=False)

    class Meta:
        db_table = 'question_options'
        verbose_name = '题目选项'
        verbose_name_plural = verbose_name
        ordering = ['question', 'order', 'label']
        unique_together = [['question', 'label']]

    def __str__(self):
        return f'{self.label}. {self.content[:20]}'
