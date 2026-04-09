"""
题目附件模型
"""
from django.db import models

from utils.mixins import TimeStampMixin
from utils.storage import get_attachment_storage


def attachment_upload_path(instance, filename):
    """
    生成附件上传路径
    格式: attachments/{question_id}/{filename}
    """
    import os
    from django.utils import timezone

    # 获取文件扩展名
    ext = os.path.splitext(filename)[1].lower()
    # 使用时间戳生成唯一文件名
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S_%f')
    new_filename = f"{timestamp}{ext}"

    # 如果有关联的题目，使用题目 ID 作为子目录
    if instance.question_id:
        return f"attachments/{instance.question_id}/{new_filename}"
    return f"attachments/temp/{new_filename}"


class Attachment(TimeStampMixin, models.Model):
    """
    题目附件模型
    支持图片、音频、视频等文件
    使用 MinIO/OSS 对象存储
    """

    class Type(models.TextChoices):
        IMAGE = 'image', '图片'
        AUDIO = 'audio', '音频'
        VIDEO = 'video', '视频'
        DOCUMENT = 'document', '文档'
        OTHER = 'other', '其他'

    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='所属题目'
    )
    name = models.CharField('文件名', max_length=255)
    file = models.FileField(
        '文件',
        upload_to=attachment_upload_path,
        storage=get_attachment_storage
    )
    type = models.CharField(
        '文件类型',
        max_length=20,
        choices=Type.choices,
        default=Type.OTHER
    )
    size = models.PositiveIntegerField('文件大小(字节)', default=0)
    mime_type = models.CharField('MIME类型', max_length=100, blank=True)
    description = models.CharField('描述', max_length=255, blank=True)

    # 存储元数据
    storage_key = models.CharField('存储键', max_length=500, blank=True, help_text='对象存储中的完整路径')
    checksum = models.CharField('文件校验和', max_length=64, blank=True, help_text='MD5 或 SHA256')

    class Meta:
        db_table = 'question_attachments'
        verbose_name = '题目附件'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.file:
            # 自动填充文件大小
            if not self.size:
                try:
                    self.size = self.file.size
                except Exception:
                    pass

            # 自动检测文件类型
            if not self.type or self.type == self.Type.OTHER:
                self.type = self._detect_file_type()

            # 保存存储键
            if not self.storage_key and hasattr(self.file, 'name'):
                self.storage_key = self.file.name

        super().save(*args, **kwargs)

    def _detect_file_type(self):
        """根据文件扩展名或 MIME 类型检测文件类型"""
        import os
        import mimetypes

        if not self.file:
            return self.Type.OTHER

        filename = self.file.name if hasattr(self.file, 'name') else str(self.file)
        ext = os.path.splitext(filename)[1].lower()

        # 检测 MIME 类型
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            self.mime_type = mime_type

        # 根据扩展名判断类型
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        audio_exts = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}
        video_exts = {'.mp4', '.webm', '.avi', '.mov', '.mkv', '.flv'}
        document_exts = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md'}

        if ext in image_exts:
            return self.Type.IMAGE
        elif ext in audio_exts:
            return self.Type.AUDIO
        elif ext in video_exts:
            return self.Type.VIDEO
        elif ext in document_exts:
            return self.Type.DOCUMENT
        else:
            return self.Type.OTHER

    def get_signed_url(self, expires=3600):
        """
        获取带签名的临时访问 URL
        
        Args:
            expires: URL 有效期（秒）
            
        Returns:
            签名后的 URL 字符串
        """
        if hasattr(self.file.storage, 'url'):
            # 对于支持签名 URL 的存储后端
            try:
                return self.file.url
            except Exception:
                pass
        return None

    def delete(self, *args, **kwargs):
        """删除附件时同时删除存储的文件"""
        # 先删除文件
        if self.file:
            try:
                self.file.delete(save=False)
            except Exception:
                pass
        # 再删除数据库记录
        super().delete(*args, **kwargs)
