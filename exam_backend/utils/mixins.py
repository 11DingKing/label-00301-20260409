"""
自定义 Mixin 类
"""
from django.db import models
from django.utils import timezone


class TimeStampMixin(models.Model):
    """
    时间戳 Mixin
    """
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    软删除 Mixin
    """
    is_deleted = models.BooleanField('是否删除', default=False)
    deleted_at = models.DateTimeField('删除时间', null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class CreatedByMixin(models.Model):
    """
    创建者 Mixin
    """
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='创建者'
    )

    class Meta:
        abstract = True


class OrderMixin(models.Model):
    """
    排序 Mixin
    """
    order = models.PositiveIntegerField('排序', default=0)

    class Meta:
        abstract = True
        ordering = ['order']


class ActiveMixin(models.Model):
    """
    启用/禁用 Mixin
    """
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        abstract = True


# ============ ViewSet Mixins ============

class MultiSerializerMixin:
    """
    多序列化器 Mixin
    支持不同 action 使用不同的序列化器
    """
    serializer_classes = {}
    serializer_class = None  # 默认序列化器

    def get_serializer_class(self):
        # 优先使用 action 对应的序列化器
        if self.action and self.action in self.serializer_classes:
            return self.serializer_classes[self.action]
        # 其次使用 default
        if 'default' in self.serializer_classes:
            return self.serializer_classes['default']
        # 最后使用 serializer_class
        if self.serializer_class:
            return self.serializer_class
        # 调用父类方法
        return super().get_serializer_class()


class MultiPermissionMixin:
    """
    多权限 Mixin
    支持不同 action 使用不同的权限
    """
    permission_classes_by_action = {}

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return super().get_permissions()
