"""
用户资料模型
"""
from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """
    用户资料扩展
    """

    class Gender(models.TextChoices):
        MALE = 'male', '男'
        FEMALE = 'female', '女'
        OTHER = 'other', '其他'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户'
    )

    # 个人信息
    real_name = models.CharField('真实姓名', max_length=50, blank=True)
    gender = models.CharField(
        '性别',
        max_length=10,
        choices=Gender.choices,
        blank=True
    )
    birthday = models.DateField('生日', blank=True, null=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('个人简介', max_length=500, blank=True)

    # 学生专属字段
    student_id = models.CharField('学号', max_length=50, blank=True)
    class_name = models.CharField('班级', max_length=100, blank=True)
    grade = models.CharField('年级', max_length=50, blank=True)
    school = models.CharField('学校', max_length=200, blank=True)

    # 教师专属字段
    employee_id = models.CharField('工号', max_length=50, blank=True)
    department = models.CharField('部门/院系', max_length=200, blank=True)
    title = models.CharField('职称', max_length=100, blank=True)

    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} 的资料'
