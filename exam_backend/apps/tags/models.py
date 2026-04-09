"""
标签和分类模型
"""
from django.db import models

from utils.mixins import TimeStampMixin, OrderMixin


class Category(TimeStampMixin, OrderMixin, models.Model):
    """
    分类模型（一级分类）
    """
    name = models.CharField('分类名称', max_length=100, unique=True)
    description = models.TextField('描述', blank=True)
    icon = models.CharField('图标', max_length=100, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父分类'
    )
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        db_table = 'categories'
        verbose_name = '分类'
        verbose_name_plural = verbose_name
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} > {self.name}'
        return self.name

    @property
    def full_path(self):
        """获取完整路径"""
        if self.parent:
            return f'{self.parent.full_path} > {self.name}'
        return self.name


class Tag(TimeStampMixin, models.Model):
    """
    标签模型
    """

    class Color(models.TextChoices):
        DEFAULT = 'default', '默认'
        PRIMARY = 'primary', '蓝色'
        SUCCESS = 'success', '绿色'
        WARNING = 'warning', '橙色'
        DANGER = 'danger', '红色'
        INFO = 'info', '青色'

    name = models.CharField('标签名称', max_length=50, unique=True)
    color = models.CharField(
        '颜色',
        max_length=20,
        choices=Color.choices,
        default=Color.DEFAULT
    )
    description = models.CharField('描述', max_length=255, blank=True)
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        db_table = 'tags'
        verbose_name = '标签'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def question_count(self):
        """关联的题目数量"""
        return self.questions.count()
