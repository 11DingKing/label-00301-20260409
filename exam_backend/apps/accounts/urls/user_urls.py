"""
用户相关 URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import UserViewSet, UserProfileView

router = DefaultRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('', include(router.urls)),
]
