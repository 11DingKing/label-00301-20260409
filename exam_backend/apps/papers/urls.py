"""
试卷 URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from apps.papers.views import PaperViewSet, PaperSectionViewSet

router = DefaultRouter()
router.register('', PaperViewSet, basename='paper')

# 嵌套路由：试卷下的大题
papers_router = routers.NestedDefaultRouter(router, '', lookup='paper')
papers_router.register('sections', PaperSectionViewSet, basename='paper-sections')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(papers_router.urls)),
]
