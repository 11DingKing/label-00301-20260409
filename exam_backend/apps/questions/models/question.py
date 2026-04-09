"""
题目模型
"""
from django.conf import settings
from django.db import models

from utils.mixins import TimeStampMixin, SoftDeleteMixin, CreatedByMixin


class Question(TimeStampMixin, SoftDeleteMixin, CreatedByMixin, models.Model):
    """
    题目模型
    支持：单选题、多选题、判断题、填空题、简答题、编程题
    """

    class Type(models.TextChoices):
        SINGLE = 'single', '单选题'
        MULTI = 'multi', '多选题'
        JUDGE = 'judge', '判断题'
        BLANK = 'blank', '填空题'
        SHORT = 'short', '简答题'
        PROGRAMMING = 'programming', '编程题'

    class Difficulty(models.IntegerChoices):
        EASY = 1, '简单'
        MEDIUM = 2, '中等'
        HARD = 3, '困难'

    # 基本信息
    title = models.TextField('题目标题')
    type = models.CharField(
        '题目类型',
        max_length=20,
        choices=Type.choices,
        default=Type.SINGLE,
        db_index=True
    )
    difficulty = models.PositiveSmallIntegerField(
        '难度',
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
        db_index=True
    )
    score = models.DecimalField('默认分值', max_digits=5, decimal_places=1, default=5)

    # 题目内容
    content = models.TextField('题目内容', blank=True, help_text='支持 Markdown')

    # 答案相关
    answer = models.TextField('标准答案', blank=True, help_text='选择题存选项ID，填空题存答案，编程题存测试用例')
    answer_analysis = models.TextField('答案解析', blank=True)

    # 编程题专用
    programming_language = models.CharField('编程语言', max_length=50, blank=True)
    time_limit = models.PositiveIntegerField('时间限制(ms)', default=1000, blank=True)
    memory_limit = models.PositiveIntegerField('内存限制(MB)', default=256, blank=True)
    test_cases = models.JSONField('测试用例', default=list, blank=True)

    # 分类
    tags = models.ManyToManyField(
        'tags.Tag',
        blank=True,
        related_name='questions',
        verbose_name='标签'
    )
    category = models.ForeignKey(
        'tags.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions',
        verbose_name='分类'
    )

    # 统计
    use_count = models.PositiveIntegerField('使用次数', default=0)
    correct_count = models.PositiveIntegerField('正确次数', default=0)

    # 状态
    is_public = models.BooleanField('是否公开', default=True)

    class Meta:
        db_table = 'questions'
        verbose_name = '题目'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type', 'difficulty']),
            models.Index(fields=['is_public', 'is_deleted']),
        ]

    def __str__(self):
        return f'[{self.get_type_display()}] {self.title[:50]}'

    @property
    def correct_rate(self):
        """正确率"""
        if self.use_count == 0:
            return 0
        return round(self.correct_count / self.use_count * 100, 2)

    @property
    def is_objective(self):
        """是否为客观题"""
        return self.type in [self.Type.SINGLE, self.Type.MULTI, self.Type.JUDGE]
