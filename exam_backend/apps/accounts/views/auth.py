"""
认证相关视图
"""
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.serializers import (
    LoginSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    UserSerializer,
)


class LoginView(APIView):
    """
    用户登录
    POST /api/v1/auth/login/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response({
            'success': True,
            'message': '登录成功',
            'data': {
                'user': UserSerializer(result['user']).data,
                'tokens': result['tokens']
            }
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    用户注册
    POST /api/v1/auth/register/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 生成 Token
        refresh = RefreshToken.for_user(user)

        return Response({
            'success': True,
            'message': '注册成功',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    用户登出
    POST /api/v1/auth/logout/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({
                'success': True,
                'message': '登出成功'
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                'success': False,
                'message': '登出失败'
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    修改密码
    POST /api/v1/auth/change-password/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'success': True,
            'message': '密码修改成功'
        }, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """
    刷新 Token
    POST /api/v1/auth/refresh/
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response({
                'success': True,
                'message': 'Token 刷新成功',
                'data': response.data
            })
        return response
