"""
自定义用户模型
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    自定义用户管理器
    """

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('用户名不能为空')
        if not email:
            raise ValueError('邮箱不能为空')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置 is_superuser=True')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    自定义用户模型
    """

    class Role(models.TextChoices):
        STUDENT = 'student', '学生'
        TEACHER = 'teacher', '教师'
        ADMIN = 'admin', '管理员'

    # 基本信息
    username = models.CharField('用户名', max_length=50, unique=True)
    email = models.EmailField('邮箱', unique=True)
    phone = models.CharField('手机号', max_length=20, blank=True, null=True)

    # 角色和状态
    role = models.CharField(
        '角色',
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )
    is_active = models.BooleanField('是否激活', default=True)
    is_staff = models.BooleanField('是否员工', default=False)

    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    last_login_ip = models.GenericIPAddressField('最后登录IP', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
