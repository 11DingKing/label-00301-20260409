"""
自定义异常处理
"""
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    统一返回格式
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': get_error_message(exc),
                'detail': response.data
            }
        }
        response.data = custom_response_data

    return response


def get_error_message(exc):
    """
    获取错误消息
    """
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, str):
            return exc.detail
        elif isinstance(exc.detail, list):
            return exc.detail[0] if exc.detail else '请求错误'
        elif isinstance(exc.detail, dict):
            for key, value in exc.detail.items():
                if isinstance(value, list):
                    return f'{key}: {value[0]}'
                return f'{key}: {value}'
    return str(exc)


# ============ 自定义异常类 ============

class ExamNotStartedException(APIException):
    """
    考试未开始异常
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '考试尚未开始'
    default_code = 'exam_not_started'


class ExamEndedException(APIException):
    """
    考试已结束异常
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '考试已结束'
    default_code = 'exam_ended'


class ExamTimeoutException(APIException):
    """
    考试超时异常
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '考试时间已用尽'
    default_code = 'exam_timeout'


class AlreadySubmittedException(APIException):
    """
    已提交异常
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '您已提交过答案'
    default_code = 'already_submitted'


class NoPermissionException(APIException):
    """
    无权限异常
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = '您没有权限执行此操作'
    default_code = 'no_permission'


class ResourceNotFoundException(APIException):
    """
    资源不存在异常
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '请求的资源不存在'
    default_code = 'resource_not_found'


class InvalidOperationException(APIException):
    """
    无效操作异常
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '无效的操作'
    default_code = 'invalid_operation'


class QuotaExceededException(APIException):
    """
    配额超限异常
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = '请求次数过多，请稍后再试'
    default_code = 'quota_exceeded'
