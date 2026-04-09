"""
公共模型
"""
from django.conf import settings
from django.db import models

from utils.mixins import TimeStampMixin


class SystemConfig(models.Model):
    """
    系统配置模型
    """
    key = models.CharField('配置键', max_length=100, unique=True)
    value = models.TextField('配置值')
    description = models.CharField('描述', max_length=255, blank=True)
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        db_table = 'system_configs'
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.key}: {self.value[:50]}'


class OperationLog(TimeStampMixin, models.Model):
    """
    操作日志模型
    """

    class Type(models.TextChoices):
        CREATE = 'create', '创建'
        UPDATE = 'update', '更新'
        DELETE = 'delete', '删除'
        LOGIN = 'login', '登录'
        LOGOUT = 'logout', '登出'
        EXPORT = 'export', '导出'
        IMPORT = 'import', '导入'
        OTHER = 'other', '其他'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operation_logs',
        verbose_name='操作用户'
    )
    type = models.CharField(
        '操作类型',
        max_length=20,
        choices=Type.choices,
        default=Type.OTHER
    )
    module = models.CharField('模块', max_length=50)
    action = models.CharField('操作', max_length=100)
    detail = models.TextField('详情', blank=True)

    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('浏览器信息', blank=True)

    # 关联对象
    object_type = models.CharField('对象类型', max_length=100, blank=True)
    object_id = models.PositiveIntegerField('对象ID', null=True, blank=True)

    class Meta:
        db_table = 'operation_logs'
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['module', 'type']),
        ]

    def __str__(self):
        return f'{self.user} - {self.action}'


class Notification(TimeStampMixin, models.Model):
    """
    通知模型
    """

    class Type(models.TextChoices):
        SYSTEM = 'system', '系统通知'
        EXAM = 'exam', '考试通知'
        GRADE = 'grade', '成绩通知'
        REMIND = 'remind', '提醒'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收用户'
    )
    type = models.CharField(
        '通知类型',
        max_length=20,
        choices=Type.choices,
        default=Type.SYSTEM
    )
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    is_read = models.BooleanField('是否已读', default=False)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)

    # 关联对象
    related_type = models.CharField('关联对象类型', max_length=50, blank=True)
    related_id = models.PositiveIntegerField('关联对象ID', null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = '通知'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.title}'


class FileUpload(TimeStampMixin, models.Model):
    """
    文件上传模型
    """

    class Type(models.TextChoices):
        IMAGE = 'image', '图片'
        DOCUMENT = 'document', '文档'
        VIDEO = 'video', '视频'
        AUDIO = 'audio', '音频'
        OTHER = 'other', '其他'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploads',
        verbose_name='上传用户'
    )
    file = models.FileField('文件', upload_to='uploads/%Y/%m/')
    original_name = models.CharField('原始文件名', max_length=255)
    type = models.CharField(
        '文件类型',
        max_length=20,
        choices=Type.choices,
        default=Type.OTHER
    )
    size = models.PositiveIntegerField('文件大小(字节)', default=0)
    mime_type = models.CharField('MIME类型', max_length=100, blank=True)

    class Meta:
        db_table = 'file_uploads'
        verbose_name = '文件上传'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.original_name
