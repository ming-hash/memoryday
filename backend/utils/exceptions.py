from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class CustomAPIException(APIException):
    """自定义API异常"""
    
    def __init__(self, detail=None, code=None, status_code=None):
        super().__init__(detail=detail, code=code)
        if status_code is not None:
            self.status_code = status_code


class ValidationError(CustomAPIException):
    """验证错误"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '验证错误'
    default_code = 'validation_error'


class AuthenticationError(CustomAPIException):
    """认证错误"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = '认证失败'
    default_code = 'authentication_error'


class PermissionDeniedError(CustomAPIException):
    """权限错误"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = '权限不足'
    default_code = 'permission_denied'


class NotFoundError(CustomAPIException):
    """资源未找到"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '资源未找到'
    default_code = 'not_found'


class InternalServerError(CustomAPIException):
    """服务器内部错误"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = '服务器内部错误'
    default_code = 'internal_server_error'


class ServiceUnavailableError(CustomAPIException):
    """服务不可用"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = '服务暂时不可用'
    default_code = 'service_unavailable'


def custom_exception_handler(exc, context):
    """
    自定义异常处理
    """
    # 调用REST Framework的默认异常处理
    response = exception_handler(exc, context)
    
    if response is not None:
        # 自定义响应格式
        response.data = {
            'success': False,
            'error': {
                'code': response.data.get('code', getattr(exc, 'default_code', 'error')),
                'message': response.data.get('detail', str(exc)),
                'details': response.data
            }
        }
        # 移除原始的detail字段
        if 'detail' in response.data['error']['details']:
            del response.data['error']['details']['detail']
    else:
        # 处理非DRF异常
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        response = JsonResponse({
            'success': False,
            'error': {
                'code': 'internal_server_error',
                'message': '服务器内部错误',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


def handle_validation_error(serializer):
    """
    处理序列化器验证错误
    """
    errors = []
    for field, field_errors in serializer.errors.items():
        for error in field_errors:
            errors.append({
                'field': field,
                'message': str(error),
                'code': error.code if hasattr(error, 'code') else 'invalid'
            })
    
    raise ValidationError({
        'code': 'validation_error',
        'message': '输入数据验证失败',
        'errors': errors
    })


class ErrorCodes:
    """错误代码常量"""
    
    # 通用错误
    UNKNOWN_ERROR = 'unknown_error'
    VALIDATION_ERROR = 'validation_error'
    AUTHENTICATION_ERROR = 'authentication_error'
    PERMISSION_DENIED = 'permission_denied'
    NOT_FOUND = 'not_found'
    METHOD_NOT_ALLOWED = 'method_not_allowed'
    INTERNAL_ERROR = 'internal_error'
    SERVICE_UNAVAILABLE = 'service_unavailable'
    
    # 业务错误
    USER_NOT_FOUND = 'user_not_found'
    DISH_NOT_FOUND = 'dish_not_found'
    TAG_NOT_FOUND = 'tag_not_found'
    FILE_NOT_FOUND = 'file_not_found'
    INVALID_CREDENTIALS = 'invalid_credentials'
    ACCOUNT_DISABLED = 'account_disabled'
    RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded'
    QUOTA_EXCEEDED = 'quota_exceeded'
    FILE_TOO_LARGE = 'file_too_large'
    UNSUPPORTED_FILE_TYPE = 'unsupported_file_type'
    INVALID_FILE = 'invalid_file'
    
    # 微信相关错误
    WECHAT_AUTH_FAILED = 'wechat_auth_failed'
    WECHAT_SESSION_EXPIRED = 'wechat_session_expired'
    WECHAT_API_ERROR = 'wechat_api_error'
    
    # 数据库错误
    DATABASE_ERROR = 'database_error'
    DUPLICATE_ENTRY = 'duplicate_entry'
    INTEGRITY_ERROR = 'integrity_error'
    
    # 网络错误
    NETWORK_ERROR = 'network_error'
    TIMEOUT_ERROR = 'timeout_error'
    CONNECTION_ERROR = 'connection_error'


def get_error_message(code, default=None):
    """
    获取错误消息
    """
    error_messages = {
        ErrorCodes.UNKNOWN_ERROR: '未知错误',
        ErrorCodes.VALIDATION_ERROR: '数据验证失败',
        ErrorCodes.AUTHENTICATION_ERROR: '认证失败',
        ErrorCodes.PERMISSION_DENIED: '权限不足',
        ErrorCodes.NOT_FOUND: '资源未找到',
        ErrorCodes.METHOD_NOT_ALLOWED: '方法不允许',
        ErrorCodes.INTERNAL_ERROR: '服务器内部错误',
        ErrorCodes.SERVICE_UNAVAILABLE: '服务不可用',
        
        ErrorCodes.USER_NOT_FOUND: '用户不存在',
        ErrorCodes.DISH_NOT_FOUND: '菜品不存在',
        ErrorCodes.TAG_NOT_FOUND: '标签不存在',
        ErrorCodes.FILE_NOT_FOUND: '文件不存在',
        ErrorCodes.INVALID_CREDENTIALS: '无效的凭证',
        ErrorCodes.ACCOUNT_DISABLED: '账户已禁用',
        ErrorCodes.RATE_LIMIT_EXCEEDED: '请求频率过高',
        ErrorCodes.QUOTA_EXCEEDED: '配额已用完',
        ErrorCodes.FILE_TOO_LARGE: '文件过大',
        ErrorCodes.UNSUPPORTED_FILE_TYPE: '不支持的文件类型',
        ErrorCodes.INVALID_FILE: '无效的文件',
        
        ErrorCodes.WECHAT_AUTH_FAILED: '微信认证失败',
        ErrorCodes.WECHAT_SESSION_EXPIRED: '微信会话已过期',
        ErrorCodes.WECHAT_API_ERROR: '微信接口调用失败',
        
        ErrorCodes.DATABASE_ERROR: '数据库错误',
        ErrorCodes.DUPLICATE_ENTRY: '重复记录',
        ErrorCodes.INTEGRITY_ERROR: '数据完整性错误',
        
        ErrorCodes.NETWORK_ERROR: '网络错误',
        ErrorCodes.TIMEOUT_ERROR: '请求超时',
        ErrorCodes.CONNECTION_ERROR: '连接错误',
    }
    
    return error_messages.get(code, default or '未知错误')