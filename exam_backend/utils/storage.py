"""
自定义存储后端
支持 MinIO / AWS S3 / 阿里云 OSS
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MinIOStorage(S3Boto3Storage):
    """
    MinIO 存储后端
    基于 S3 兼容 API
    """
    bucket_name = getattr(settings, 'MINIO_STORAGE_BUCKET_NAME', 'exam-files')
    custom_domain = None  # MinIO 不使用自定义域名
    file_overwrite = False
    default_acl = 'private'
    querystring_auth = True  # 使用签名 URL
    querystring_expire = 3600  # URL 过期时间（秒）

    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = kwargs.get('bucket_name', self.bucket_name)
        super().__init__(*args, **kwargs)


class PublicMinIOStorage(MinIOStorage):
    """
    公开访问的 MinIO 存储
    用于不需要权限控制的静态资源
    """
    default_acl = 'public-read'
    querystring_auth = False


class PrivateMinIOStorage(MinIOStorage):
    """
    私有 MinIO 存储
    用于需要权限控制的文件（如答案、附件等）
    """
    default_acl = 'private'
    querystring_auth = True


class AliyunOSSStorage(S3Boto3Storage):
    """
    阿里云 OSS 存储后端
    """
    bucket_name = getattr(settings, 'ALIYUN_OSS_BUCKET_NAME', 'exam-files')
    custom_domain = getattr(settings, 'ALIYUN_OSS_CUSTOM_DOMAIN', None)
    file_overwrite = False
    default_acl = 'private'
    querystring_auth = True
    querystring_expire = 3600

    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = kwargs.get('bucket_name', self.bucket_name)
        super().__init__(*args, **kwargs)


def get_storage_class():
    """
    根据配置返回适当的存储类
    """
    storage_backend = getattr(settings, 'FILE_STORAGE_BACKEND', 'local')

    if storage_backend == 'minio':
        return MinIOStorage
    elif storage_backend == 'aliyun_oss':
        return AliyunOSSStorage
    elif storage_backend == 's3':
        return S3Boto3Storage
    else:
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage


# 预定义的存储实例
def get_attachment_storage():
    """获取附件存储实例"""
    storage_backend = getattr(settings, 'FILE_STORAGE_BACKEND', 'local')

    if storage_backend == 'minio':
        return PrivateMinIOStorage(
            bucket_name=getattr(settings, 'MINIO_ATTACHMENTS_BUCKET', 'exam-attachments')
        )
    elif storage_backend == 'aliyun_oss':
        return AliyunOSSStorage(
            bucket_name=getattr(settings, 'ALIYUN_OSS_ATTACHMENTS_BUCKET', 'exam-attachments')
        )
    elif storage_backend == 's3':
        return S3Boto3Storage(
            bucket_name=getattr(settings, 'AWS_ATTACHMENTS_BUCKET', 'exam-attachments')
        )
    else:
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage()


def get_media_storage():
    """获取媒体文件存储实例"""
    storage_backend = getattr(settings, 'FILE_STORAGE_BACKEND', 'local')

    if storage_backend == 'minio':
        return PublicMinIOStorage(
            bucket_name=getattr(settings, 'MINIO_MEDIA_BUCKET', 'exam-media')
        )
    elif storage_backend == 'aliyun_oss':
        return AliyunOSSStorage(
            bucket_name=getattr(settings, 'ALIYUN_OSS_MEDIA_BUCKET', 'exam-media')
        )
    elif storage_backend == 's3':
        return S3Boto3Storage(
            bucket_name=getattr(settings, 'AWS_MEDIA_BUCKET', 'exam-media')
        )
    else:
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage()
