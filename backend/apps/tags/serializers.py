from rest_framework import serializers
from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'tag_type', 'dish_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'dish_count', 'created_at', 'updated_at']