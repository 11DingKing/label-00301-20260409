"""
公共组件 URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.commons.views import (
    SystemConfigViewSet,
    OperationLogViewSet,
    NotificationViewSet,
    FileUploadViewSet,
)

router = DefaultRouter()
router.register('configs', SystemConfigViewSet, basename='config')
router.register('logs', OperationLogViewSet, basename='log')
router.register('notifications', NotificationViewSet, basename='notification')
router.register('files', FileUploadViewSet, basename='file')

urlpatterns = [
    path('', include(router.urls)),
]
