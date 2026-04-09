"""
考试-试卷关联模型

注意：目前 Exam 模型直接通过 ForeignKey 关联 Paper，
此文件作为占位文件，以符合项目结构规范。
如果未来需要更复杂的关联逻辑（如同一试卷的多个版本配置等），
可以在此文件中定义 ExamPaper 中间表模型。
"""

# 当前 Exam 与 Paper 的关联通过 Exam 模型中的 ForeignKey 实现
# 如需扩展，可在此定义中间表：
#
# from django.db import models
# from utils.mixins import TimeStampMixin
#
#
# class ExamPaper(TimeStampMixin, models.Model):
#     """
#     考试-试卷关联模型（中间表）
#     支持同一试卷在不同考试中使用不同配置
#     """
#     exam = models.ForeignKey(
#         'exams.Exam',
#         on_delete=models.CASCADE,
#         related_name='exam_papers',
#         verbose_name='考试'
#     )
#     paper = models.ForeignKey(
#         'papers.Paper',
#         on_delete=models.CASCADE,
#         related_name='exam_papers',
#         verbose_name='试卷'
#     )
#     # 可添加考试特定的试卷配置
#     time_limit_override = models.PositiveIntegerField('时长覆盖(分钟)', null=True, blank=True)
#     pass_score_override = models.DecimalField('及格分覆盖', max_digits=5, decimal_places=1, null=True, blank=True)
#
#     class Meta:
#         db_table = 'exam_papers'
#         verbose_name = '考试试卷关联'
#         verbose_name_plural = verbose_name
#         unique_together = [['exam', 'paper']]
