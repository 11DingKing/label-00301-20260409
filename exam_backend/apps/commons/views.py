"""
公共视图
"""
import mimetypes

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.commons.models import SystemConfig, OperationLog, Notification, FileUpload
from apps.commons.serializers import (
    SystemConfigSerializer,
    OperationLogSerializer,
    NotificationSerializer,
    FileUploadSerializer,
)
from utils.permissions import IsAdmin


class SystemConfigViewSet(viewsets.ModelViewSet):
    """
    系统配置视图集
    """
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'key'

    @action(detail=False, methods=['get'])
    def public(self, request):
        """
        获取公开配置（无需登录）
        GET /api/v1/commons/configs/public/
        """
        configs = SystemConfig.objects.filter(
            is_active=True,
            key__startswith='public_'
        )
        serializer = SystemConfigSerializer(configs, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    操作日志视图集
    """
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['user', 'type', 'module']
    search_fields = ['action', 'detail']
    ordering = ['-created_at']


class NotificationViewSet(viewsets.ModelViewSet):
    """
    通知视图集
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        获取未读通知
        GET /api/v1/commons/notifications/unread/
        """
        notifications = self.get_queryset().filter(is_read=False)
        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'unread_count': notifications.count()
        })

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        标记所有为已读
        POST /api/v1/commons/notifications/mark_all_read/
        """
        self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({
            'success': True,
            'message': '已全部标记为已读'
        })

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        标记单个为已读
        POST /api/v1/commons/notifications/{id}/mark_read/
        """
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at'])
        return Response({
            'success': True,
            'message': '已标记为已读'
        })


class FileUploadViewSet(viewsets.ModelViewSet):
    """
    文件上传视图集
    """
    serializer_class = FileUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return FileUpload.objects.all()
        return FileUpload.objects.filter(user=user)

    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        if file:
            # 获取文件类型
            mime_type, _ = mimetypes.guess_type(file.name)
            file_type = 'other'
            if mime_type:
                if mime_type.startswith('image'):
                    file_type = 'image'
                elif mime_type.startswith('video'):
                    file_type = 'video'
                elif mime_type.startswith('audio'):
                    file_type = 'audio'
                elif 'document' in mime_type or 'pdf' in mime_type or 'word' in mime_type:
                    file_type = 'document'

            serializer.save(
                user=self.request.user,
                original_name=file.name,
                type=file_type,
                size=file.size,
                mime_type=mime_type or ''
            )
        else:
            serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def batch_upload(self, request):
        """
        批量上传
        POST /api/v1/commons/files/batch_upload/
        """
        files = request.FILES.getlist('files')
        if not files:
            return Response({
                'success': False,
                'message': '请选择文件'
            }, status=status.HTTP_400_BAD_REQUEST)

        uploaded = []
        for file in files:
            mime_type, _ = mimetypes.guess_type(file.name)
            file_type = 'other'
            if mime_type:
                if mime_type.startswith('image'):
                    file_type = 'image'
                elif mime_type.startswith('video'):
                    file_type = 'video'
                elif mime_type.startswith('audio'):
                    file_type = 'audio'

            upload = FileUpload.objects.create(
                user=request.user,
                file=file,
                original_name=file.name,
                type=file_type,
                size=file.size,
                mime_type=mime_type or ''
            )
            uploaded.append(upload)

        serializer = FileUploadSerializer(uploaded, many=True, context={'request': request})
        return Response({
            'success': True,
            'message': f'成功上传 {len(uploaded)} 个文件',
            'data': serializer.data
        })
