"""
用户相关序列化器
"""
from rest_framework import serializers

from apps.accounts.models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户资料序列化器
    """

    class Meta:
        model = UserProfile
        fields = [
            'real_name', 'gender', 'birthday', 'avatar', 'bio',
            'student_id', 'class_name', 'grade', 'school',
            'employee_id', 'department', 'title'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    用户详情序列化器
    """
    profile = UserProfileSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone',
            'role', 'role_display', 'is_active',
            'created_at', 'updated_at', 'last_login',
            'profile'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']


class UserListSerializer(serializers.ModelSerializer):
    """
    用户列表序列化器（简化版）
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'role_display', 'is_active', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户更新序列化器
    """
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['email', 'phone', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)

        # 更新用户基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新用户资料
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance
