"""
统计数据模型
"""
from django.conf import settings
from django.db import models

from utils.mixins import TimeStampMixin


class ExamStatistics(TimeStampMixin, models.Model):
    """
    考试统计数据模型
    """
    exam = models.OneToOneField(
        'exams.Exam',
        on_delete=models.CASCADE,
        related_name='statistics',
        verbose_name='考试'
    )

    # 参与统计
    participant_count = models.PositiveIntegerField('参与人数', default=0)
    submitted_count = models.PositiveIntegerField('提交人数', default=0)
    graded_count = models.PositiveIntegerField('已批改人数', default=0)

    # 成绩统计
    average_score = models.DecimalField('平均分', max_digits=6, decimal_places=2, null=True)
    highest_score = models.DecimalField('最高分', max_digits=6, decimal_places=2, null=True)
    lowest_score = models.DecimalField('最低分', max_digits=6, decimal_places=2, null=True)
    median_score = models.DecimalField('中位数', max_digits=6, decimal_places=2, null=True)
    pass_rate = models.DecimalField('及格率', max_digits=5, decimal_places=2, null=True)

    # 分数分布
    score_distribution = models.JSONField('分数分布', default=dict, blank=True)

    # 题目统计
    question_stats = models.JSONField('题目统计', default=dict, blank=True)

    class Meta:
        db_table = 'exam_statistics'
        verbose_name = '考试统计'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.exam.title} 统计'


class UserStatistics(TimeStampMixin, models.Model):
    """
    用户学习统计模型
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_statistics',
        verbose_name='用户'
    )

    # 考试统计
    exam_count = models.PositiveIntegerField('参加考试次数', default=0)
    passed_count = models.PositiveIntegerField('及格次数', default=0)
    total_score = models.DecimalField('总得分', max_digits=10, decimal_places=2, default=0)
    average_score = models.DecimalField('平均分', max_digits=6, decimal_places=2, null=True)

    # 题目统计
    question_count = models.PositiveIntegerField('答题数', default=0)
    correct_count = models.PositiveIntegerField('正确数', default=0)
    accuracy_rate = models.DecimalField('正确率', max_digits=5, decimal_places=2, null=True)

    # 学习时长
    total_duration = models.PositiveIntegerField('总学习时长(秒)', default=0)

    # 弱项标签
    weak_tags = models.JSONField('弱项标签', default=list, blank=True)

    class Meta:
        db_table = 'user_statistics'
        verbose_name = '用户统计'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} 统计'
