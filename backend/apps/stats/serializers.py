from rest_framework import serializers
from .models import UserStat


class UserStatSerializer(serializers.ModelSerializer):
    """用户统计序列化器"""
    class Meta:
        model = UserStat
        fields = ['id', 'user', 'date', 'dishes_created', 'dishes_viewed', 'time_spent', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']