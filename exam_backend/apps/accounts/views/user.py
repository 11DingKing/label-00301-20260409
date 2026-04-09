"""
用户相关视图
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User, UserProfile
from apps.accounts.serializers import (
    UserSerializer,
    UserListSerializer,
    UserProfileSerializer,
)
from apps.accounts.serializers.user import UserUpdateSerializer
from utils.permissions import IsAdmin, IsOwnerOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    """
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'phone']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'create', 'destroy']:
            return [IsAdmin()]
        if self.action in ['retrieve', 'update', 'partial_update']:
            return [IsOwnerOrAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        获取当前用户信息
        GET /api/v1/users/me/
        """
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['patch'])
    def update_me(self, request):
        """
        更新当前用户信息
        PATCH /api/v1/users/update_me/
        """
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'success': True,
            'message': '更新成功',
            'data': UserSerializer(request.user).data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def toggle_active(self, request, pk=None):
        """
        启用/禁用用户
        POST /api/v1/users/{id}/toggle_active/
        """
        user = self.get_object()
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])

        return Response({
            'success': True,
            'message': f'用户已{"启用" if user.is_active else "禁用"}',
            'data': {'is_active': user.is_active}
        })


class UserProfileView(APIView):
    """
    用户资料视图
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        获取当前用户资料
        GET /api/v1/users/profile/
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)

        return Response({
            'success': True,
            'data': serializer.data
        })

    def patch(self, request):
        """
        更新当前用户资料
        PATCH /api/v1/users/profile/
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'success': True,
            'message': '资料更新成功',
            'data': serializer.data
        })
