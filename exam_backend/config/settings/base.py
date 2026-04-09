"""
Django base settings for exam_backend project.
通用配置 - 所有环境共享
"""

import os
from datetime import timedelta
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.questions',
    'apps.exams',
    'apps.papers',
    'apps.submissions',
    'apps.grading',
    'apps.statistics',
    'apps.tags',
    'apps.commons',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============ Django REST Framework 配置 ============
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}

# ============ SimpleJWT 配置 ============
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',
}

# ============ drf-spectacular 配置 (API 文档) ============
SPECTACULAR_SETTINGS = {
    'TITLE': '在线考试系统 API',
    'DESCRIPTION': '企业级在线考试与刷题系统后端 API 文档',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v1',
}

# ============ CORS 配置 ============
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

# ============ Celery 配置 ============
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = config('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# ============ 对象存储配置 (MinIO / S3 / OSS) ============
# 存储后端选择: 'local', 'minio', 's3', 'aliyun_oss'
FILE_STORAGE_BACKEND = config('FILE_STORAGE_BACKEND', default='local')

# MinIO 配置
if FILE_STORAGE_BACKEND == 'minio':
    AWS_ACCESS_KEY_ID = config('MINIO_ACCESS_KEY', default='minioadmin')
    AWS_SECRET_ACCESS_KEY = config('MINIO_SECRET_KEY', default='minioadmin')
    AWS_S3_ENDPOINT_URL = config('MINIO_ENDPOINT', default='http://localhost:9000')
    AWS_S3_REGION_NAME = config('MINIO_REGION', default='us-east-1')
    AWS_S3_USE_SSL = config('MINIO_USE_SSL', default=False, cast=bool)
    AWS_S3_VERIFY = config('MINIO_VERIFY_SSL', default=False, cast=bool)
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 3600

    # MinIO 存储桶配置
    MINIO_STORAGE_BUCKET_NAME = config('MINIO_BUCKET', default='exam-files')
    MINIO_ATTACHMENTS_BUCKET = config('MINIO_ATTACHMENTS_BUCKET', default='exam-attachments')
    MINIO_MEDIA_BUCKET = config('MINIO_MEDIA_BUCKET', default='exam-media')

    # 使用自定义存储后端
    DEFAULT_FILE_STORAGE = 'utils.storage.MinIOStorage'

# AWS S3 配置
elif FILE_STORAGE_BACKEND == 's3':
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='exam-files')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default=None)
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 3600

    # S3 存储桶配置
    AWS_ATTACHMENTS_BUCKET = config('AWS_ATTACHMENTS_BUCKET', default='exam-attachments')
    AWS_MEDIA_BUCKET = config('AWS_MEDIA_BUCKET', default='exam-media')

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# 阿里云 OSS 配置
elif FILE_STORAGE_BACKEND == 'aliyun_oss':
    AWS_ACCESS_KEY_ID = config('ALIYUN_OSS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = config('ALIYUN_OSS_ACCESS_KEY_SECRET', default='')
    AWS_S3_ENDPOINT_URL = config('ALIYUN_OSS_ENDPOINT', default='https://oss-cn-hangzhou.aliyuncs.com')
    AWS_S3_REGION_NAME = config('ALIYUN_OSS_REGION', default='oss-cn-hangzhou')
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True
    AWS_S3_SIGNATURE_VERSION = 's3v4'

    # OSS 存储桶配置
    ALIYUN_OSS_BUCKET_NAME = config('ALIYUN_OSS_BUCKET_NAME', default='exam-files')
    ALIYUN_OSS_ATTACHMENTS_BUCKET = config('ALIYUN_OSS_ATTACHMENTS_BUCKET', default='exam-attachments')
    ALIYUN_OSS_MEDIA_BUCKET = config('ALIYUN_OSS_MEDIA_BUCKET', default='exam-media')
    ALIYUN_OSS_CUSTOM_DOMAIN = config('ALIYUN_OSS_CUSTOM_DOMAIN', default=None)

    DEFAULT_FILE_STORAGE = 'utils.storage.AliyunOSSStorage'

# ============ Elasticsearch 配置（可选） ============
USE_ELASTICSEARCH = config('USE_ELASTICSEARCH', default=False, cast=bool)
if USE_ELASTICSEARCH:
    ELASTICSEARCH_HOSTS = config('ELASTICSEARCH_HOSTS', default='http://localhost:9200').split(',')
    ELASTICSEARCH_USERNAME = config('ELASTICSEARCH_USERNAME', default='')
    ELASTICSEARCH_PASSWORD = config('ELASTICSEARCH_PASSWORD', default='')
    ELASTICSEARCH_QUESTION_INDEX = config('ELASTICSEARCH_QUESTION_INDEX', default='questions')

# ============ 日志配置 ============
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 确保日志目录存在
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
