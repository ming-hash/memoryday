from rest_framework import serializers
from .models import Dish, DishTag


class DishTagSerializer(serializers.ModelSerializer):
    """菜品标签序列化器"""
    
    class Meta:
        model = DishTag
        fields = ['id', 'name', 'description', 'dish_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'dish_count', 'created_at', 'updated_at']


class DishSerializer(serializers.ModelSerializer):
    """菜品序列化器"""
    tags = DishTagSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source='author.nickname', read_only=True, default='')
    user_avatar = serializers.CharField(source='author.avatar', read_only=True, default='')
    
    class Meta:
        model = Dish
        fields = [
            'id', 'name', 'description', 'story', 'ingredients', 'seasonings',
            'steps', 'cooking_time', 'difficulty', 'cooking_method', 'cuisine_type',
            'category', 'tags', 'main_image', 'images', 'video_url',
            'author', 'user_nickname', 'user_avatar',
            'is_public', 'is_active', 'rating', 'cooked_count', 'view_count',
            'favorite_count', 'share_count', 'tips', 'calories',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class DishCreateSerializer(serializers.ModelSerializer):
    """菜品创建序列化器"""
    tags = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Dish
        fields = [
            'name', 'description', 'story', 'ingredients', 'seasonings',
            'steps', 'cooking_time', 'difficulty', 'cooking_method', 'cuisine_type',
            'category', 'tags', 'main_image', 'images', 'video_url',
            'is_public', 'tips', 'calories'
        ]

    def create(self, validated_data):
        """创建菜品并处理标签"""
        tags_data = validated_data.pop('tags', [])
        dish = Dish.objects.create(**validated_data)
        
        # 处理标签 - 使用 DishTag 模型
        for tag_name in tags_data:
            tag, created = DishTag.objects.get_or_create(name=tag_name.strip())
            dish.tags.add(tag)
        
        return dish

    def update(self, instance, validated_data):
        """更新菜品并处理标签"""
        tags_data = validated_data.pop('tags', None)
        
        # 更新基本字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 处理标签更新
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag, created = DishTag.objects.get_or_create(name=tag_name.strip())
                instance.tags.add(tag)
        
        return instance