"""
答题记录 URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.submissions.views import SubmitViewSet, AnswerViewSet

router = DefaultRouter()
# 提交相关操作 - POST /api/submissions/{exam_id}/submit/
router.register('', SubmitViewSet, basename='submission')
# 答题记录查询 - GET /api/submissions/answers/
router.register('answers', AnswerViewSet, basename='answer')

urlpatterns = [
    path('', include(router.urls)),
]
