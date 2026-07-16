"""
自定义JWT认证类 - 优雅处理无效token
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import exceptions
import logging

logger = logging.getLogger(__name__)


class FlexibleJWTAuthentication(JWTAuthentication):
    """
    灵活的JWT认证类
    
    与标准JWTAuthentication的区别：
    - 当token无效/过期时，不会抛出AuthenticationFailed导致401
    - 而是返回None，让请求以未认证用户身份继续
    - 这样公开的GET端点（如/api/dishes/）在发送了过期token时仍然可以正常工作
    - 需要认证的端点仍然会由权限类检查并返回401/403
    """

    def authenticate(self, request):
        """
        尝试认证请求，如果token无效则优雅降级为未认证用户
        """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except (InvalidToken, TokenError, exceptions.AuthenticationFailed) as e:
            # token无效或过期，记录日志但不阻断请求
            logger.debug(f"JWT authentication skipped (invalid/expired token): {e}")
            return None

        return self.get_user(validated_token), validated_token
