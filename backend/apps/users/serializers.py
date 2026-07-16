from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'phone', 'nickname', 'avatar', 
                 'gender', 'birthday', 'openid', 'date_joined', 'updated_at']
        read_only_fields = ['id', 'openid', 'date_joined', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 
                 'nickname', 'gender', 'birthday']

    def validate(self, data):
        """验证密码确认"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('两次密码输入不一致')
        return data

    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """验证用户登录"""
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                raise serializers.ValidationError('用户账户已禁用')
            raise serializers.ValidationError('用户名或密码错误')
        
        raise serializers.ValidationError('必须提供用户名和密码')


class WechatLoginSerializer(serializers.Serializer):
    """微信登录序列化器"""
    code = serializers.CharField(required=True, max_length=100)

    def validate_code(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('微信登录code不能为空')
        return value.strip()