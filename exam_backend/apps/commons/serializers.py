"""
公共序列化器
"""
from rest_framework import serializers

from apps.commons.models import SystemConfig, OperationLog, Notification, FileUpload


class SystemConfigSerializer(serializers.ModelSerializer):
    """
    系统配置序列化器
    """

    class Meta:
        model = SystemConfig
        fields = ['id', 'key', 'value', 'description', 'is_active']


class OperationLogSerializer(serializers.ModelSerializer):
    """
    操作日志序列化器
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = OperationLog
        fields = [
            'id', 'user', 'user_name', 'type', 'type_display',
            'module', 'action', 'detail', 'ip_address',
            'object_type', 'object_id', 'created_at'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    """
    通知序列化器
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'type_display', 'title', 'content',
            'is_read', 'read_at', 'related_type', 'related_id', 'created_at'
        ]


class FileUploadSerializer(serializers.ModelSerializer):
    """
    文件上传序列化器
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = FileUpload
        fields = [
            'id', 'file', 'url', 'original_name', 'type', 'type_display',
            'size', 'mime_type', 'created_at'
        ]

    def get_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
