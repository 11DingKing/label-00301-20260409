"""
自定义权限类
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    仅管理员可访问
    """
    message = '需要管理员权限'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsTeacher(permissions.BasePermission):
    """
    仅教师可访问
    """
    message = '需要教师权限'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'teacher'


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    教师或管理员可访问
    """
    message = '需要教师或管理员权限'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['teacher', 'admin']


class IsStudent(permissions.BasePermission):
    """
    仅学生可访问
    """
    message = '需要学生权限'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'student'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    对象所有者或管理员可访问
    """
    message = '您没有权限访问此资源'

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        # 对象需要有 user 字段
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return False


class IsOwnerOrTeacher(permissions.BasePermission):
    """
    对象所有者或教师可访问
    """
    message = '您没有权限访问此资源'

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['teacher', 'admin']:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'student'):
            return obj.student == request.user
        return False


class ReadOnly(permissions.BasePermission):
    """
    只读权限
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    认证用户可写，未认证用户只读
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
