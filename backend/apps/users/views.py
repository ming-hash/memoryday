from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
import requests
import random

from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer, WechatLoginSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_sms_code(request):
    """发送短信验证码（开发环境简化版本）"""
    phone = request.data.get('phone')
    
    if not phone:
        return Response({'error': '请输入手机号'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not phone.startswith('1') or len(phone) != 11:
        return Response({'error': '请输入正确的手机号'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 生成6位验证码
    code = str(random.randint(100000, 999999))
    
    # 在开发环境中，直接返回验证码（实际项目需要接入短信服务）
    # 存储到缓存用于验证
    cache.set(f'sms_code:{phone}', code, timeout=300)  # 5分钟有效期
    
    # 打印验证码到控制台（开发环境）
    print(f"【开发环境】向 {phone} 发送验证码: {code}")
    
    return Response({
        'message': '验证码已发送',
        'code': code if __import__('os').environ.get('DEBUG', 'True').lower() == 'true' else None,
        'expire': 300
    })


class UserListView(generics.ListAPIView):
    """用户列表视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserDetailView(generics.RetrieveUpdateAPIView):
    """用户详情视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """用户注册"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """用户登录"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # 使用 phone 字段查找用户
        try:
            user = User.objects.get(phone=phone)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
        except User.DoesNotExist:
            pass
        
        return Response(
            {'error': '用户名或密码错误'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def logout_user(request):
    """用户登出"""
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': '登出成功'})
    except Exception:
        return Response(
            {'error': '无效的token'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def wechat_login(request):
    """微信登录 - 使用wx.login的code换取openid并登录/注册"""
    from django.conf import settings as django_settings
    
    serializer = WechatLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    code = serializer.validated_data['code']
    
    # 获取微信配置
    appid = getattr(django_settings, 'WECHAT_APPID', '') or __import__('os').environ.get('WECHAT_APPID', '')
    secret = getattr(django_settings, 'WECHAT_SECRET', '') or __import__('os').environ.get('WECHAT_SECRET', '')
    
    if not appid or not secret:
        return Response(
            {'error': '微信登录未配置，请在后端设置WECHAT_APPID和WECHAT_SECRET'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # 调用微信API换取openid
    try:
        wx_response = requests.get(
            'https://api.weixin.qq.com/sns/jscode2session',
            params={
                'appid': appid,
                'secret': secret,
                'js_code': code,
                'grant_type': 'authorization_code'
            },
            timeout=10
        )
        wx_data = wx_response.json()
    except Exception as e:
        return Response(
            {'error': f'调用微信API失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    if 'errcode' in wx_data and wx_data['errcode'] != 0:
        return Response(
            {'error': f'微信登录失败: {wx_data.get("errmsg", "未知错误")}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    openid = wx_data.get('openid')
    unionid = wx_data.get('unionid', '')
    session_key = wx_data.get('session_key', '')
    
    if not openid:
        return Response(
            {'error': '获取微信openid失败'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 查找或创建用户
    try:
        user = User.objects.get(openid=openid)
        # 更新最后登录时间
        user.update_login_time()
    except User.DoesNotExist:
        # 创建新用户 - 使用openid作为唯一标识
        # phone字段是必填且unique，使用临时占位值
        temp_phone = f'wx_{openid[-8:]}'
        # 确保phone不重复
        while User.objects.filter(phone=temp_phone).exists():
            import uuid
            temp_phone = f'wx_{uuid.uuid4().hex[:8]}'
        
        user = User.objects.create_user(
            phone=temp_phone,
            password=None,
            openid=openid,
            unionid=unionid,
            wechat_info={
                'session_key': session_key,
                'openid': openid,
            }
        )
    
    # 生成JWT
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })