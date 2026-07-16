from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from apps.users.models import User


class TagCategory(models.Model):
    """标签分类"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标')
    color = models.CharField(max_length=20, blank=True, verbose_name='颜色')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='排序顺序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 统计信息
    tag_count = models.PositiveIntegerField(default=0, verbose_name='标签数量')
    usage_count = models.PositiveIntegerField(default=0, verbose_name='使用次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'tag_categories'
        verbose_name = '标签分类'
        verbose_name_plural = '标签分类'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def update_stats(self):
        """更新分类统计信息"""
        self.tag_count = self.tags.filter(is_active=True).count()
        self.usage_count = sum(tag.usage_count for tag in self.tags.all())
        self.save()


class Tag(models.Model):
    """标签模型"""
    
    TAG_TYPES = [
        ('ingredient', '食材'),
        ('cooking_method', '烹饪方法'),
        ('cuisine', '菜系'),
        ('occasion', '场合'),
        ('diet', '饮食类型'),
        ('flavor', '口味'),
        ('difficulty', '难度'),
        ('time', '时间'),
        ('custom', '自定义'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    description = models.TextField(blank=True, verbose_name='标签描述')
    tag_type = models.CharField(max_length=20, choices=TAG_TYPES, verbose_name='标签类型')
    
    # 分类信息
    category = models.ForeignKey(
        TagCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tags',
        verbose_name='分类'
    )
    
    # 显示属性
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标')
    color = models.CharField(max_length=20, blank=True, verbose_name='颜色')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 统计信息
    usage_count = models.PositiveIntegerField(default=0, verbose_name='使用次数')
    dish_count = models.PositiveIntegerField(default=0, verbose_name='关联菜品数')
    user_count = models.PositiveIntegerField(default=0, verbose_name='使用用户数')
    
    # 搜索优化
    search_keywords = models.JSONField(default=list, verbose_name='搜索关键词')
    synonyms = models.JSONField(default=list, verbose_name='同义词')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'tags'
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['tag_type', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['tag_type']),
            models.Index(fields=['category']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['usage_count']),
        ]
    
    def __str__(self):
        return f'{self.get_tag_type_display()}: {self.name}'
    
    def update_stats(self):
        """更新标签统计信息"""
        from apps.dishes.models import Dish
        self.dish_count = self.dishes.count()
        self.user_count = User.objects.filter(
            created_dishes__tags=self
        ).distinct().count()
        self.save()


class UserTagPreference(models.Model):
    """用户标签偏好"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tag_preferences',
        verbose_name='用户'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='user_preferences',
        verbose_name='标签'
    )
    
    # 偏好权重
    weight = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name='偏好权重'
    )
    usage_count = models.PositiveIntegerField(default=0, verbose_name='使用次数')
    last_used = models.DateTimeField(null=True, blank=True, verbose_name='最后使用时间')
    
    # 用户评分
    user_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='用户评分'
    )
    is_favorite = models.BooleanField(default=False, verbose_name='是否收藏')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'user_tag_preferences'
        verbose_name = '用户标签偏好'
        verbose_name_plural = '用户标签偏好'
        unique_together = ['user', 'tag']
        ordering = ['-weight', '-usage_count']
    
    def __str__(self):
        return f'{self.user} - {self.tag}: {self.weight}'


class TagUsageHistory(models.Model):
    """标签使用历史"""
    
    USAGE_TYPES = [
        ('dish_creation', '创建菜品'),
        ('dish_search', '搜索菜品'),
        ('dish_filter', '筛选菜品'),
        ('preference_update', '更新偏好'),
        ('other', '其他'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tag_usage_history',
        verbose_name='用户'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='usage_history',
        verbose_name='标签'
    )
    
    # 使用信息
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES, verbose_name='使用类型')
    context = models.JSONField(default=dict, verbose_name='使用上下文')
    dish = models.ForeignKey(
        'dishes.Dish',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tag_usages',
        verbose_name='关联菜品'
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'tag_usage_history'
        verbose_name = '标签使用历史'
        verbose_name_plural = '标签使用历史'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'tag']),
            models.Index(fields=['usage_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.user} 使用了 {self.tag} - {self.get_usage_type_display()}'


class TagSynonym(models.Model):
    """标签同义词"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_synonyms',
        verbose_name='主标签'
    )
    synonym = models.CharField(max_length=50, verbose_name='同义词')
    language = models.CharField(max_length=10, default='zh', verbose_name='语言')
    is_primary = models.BooleanField(default=False, verbose_name='是否主要同义词')
    confidence = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='置信度'
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'tag_synonyms'
        verbose_name = '标签同义词'
        verbose_name_plural = '标签同义词'
        unique_together = ['tag', 'synonym', 'language']
        ordering = ['tag', '-confidence']
    
    def __str__(self):
        return f'{self.tag.name} -> {self.synonym}'


class TagRecommendation(models.Model):
    """标签推荐"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recommendations_made',
        verbose_name='源标签'
    )
    target_tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recommendations_received',
        verbose_name='目标标签'
    )
    
    # 推荐权重
    weight = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='推荐权重'
    )
    confidence = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='置信度'
    )
    
    # 推荐原因
    reason_type = models.CharField(
        max_length=20,
        choices=[
            ('co_occurrence', '共同出现'),
            ('user_preference', '用户偏好'),
            ('semantic_similarity', '语义相似'),
            ('category_based', '分类相关'),
            ('popularity', '流行度'),
            ('other', '其他'),
        ],
        verbose_name='推荐原因类型'
    )
    reason_data = models.JSONField(default=dict, verbose_name='推荐原因数据')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'tag_recommendations'
        verbose_name = '标签推荐'
        verbose_name_plural = '标签推荐'
        unique_together = ['source_tag', 'target_tag']
        ordering = ['-weight', '-confidence']
    
    def __str__(self):
        return f'{self.source_tag.name} → {self.target_tag.name} ({self.weight})'