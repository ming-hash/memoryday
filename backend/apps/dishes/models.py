from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from apps.users.models import User


class DishCategory(models.Model):
    """菜品分类"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标')
    color = models.CharField(max_length=20, blank=True, verbose_name='颜色')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='排序顺序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 统计信息
    dish_count = models.PositiveIntegerField(default=0, verbose_name='菜品数量')
    total_cooked_count = models.PositiveIntegerField(default=0, verbose_name='总烹饪次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'dish_categories'
        verbose_name = '菜品分类'
        verbose_name_plural = '菜品分类'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def update_stats(self):
        """更新分类统计信息"""
        self.dish_count = self.dishes.filter(is_active=True).count()
        self.total_cooked_count = self.dishes.aggregate(
            total=models.Sum('cooked_count')
        )['total'] or 0
        self.save()


class DishTag(models.Model):
    """菜品标签"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    description = models.TextField(blank=True, verbose_name='标签描述')
    color = models.CharField(max_length=20, blank=True, verbose_name='颜色')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 统计信息
    dish_count = models.PositiveIntegerField(default=0, verbose_name='使用次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'dish_tags'
        verbose_name = '菜品标签'
        verbose_name_plural = '菜品标签'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def update_stats(self):
        """更新标签统计信息"""
        self.dish_count = self.dishes.count()
        self.save()


class Dish(models.Model):
    """菜品模型"""
    
    DIFFICULTY_LEVELS = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
        ('expert', '专家'),
    ]
    
    COOKING_METHODS = [
        ('stir_fry', '炒'),
        ('steam', '蒸'),
        ('boil', '煮'),
        ('fry', '炸'),
        ('bake', '烤'),
        ('stew', '炖'),
        ('roast', '烤'),
        ('grill', '烧烤'),
        ('raw', '生食'),
        ('other', '其他'),
    ]
    
    CUISINE_TYPES = [
        ('chinese', '中式'),
        ('western', '西式'),
        ('japanese', '日式'),
        ('korean', '韩式'),
        ('thai', '泰式'),
        ('indian', '印度'),
        ('vietnamese', '越南'),
        ('other', '其他'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='菜品名称')
    description = models.TextField(blank=True, verbose_name='菜品描述')
    story = models.TextField(blank=True, verbose_name='菜品故事')
    
    # 基本信息
    cooking_time = models.PositiveIntegerField(verbose_name='烹饪时间(分钟)')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, verbose_name='难度')
    cooking_method = models.CharField(max_length=20, choices=COOKING_METHODS, verbose_name='烹饪方法')
    cuisine_type = models.CharField(max_length=20, choices=CUISINE_TYPES, verbose_name='菜系')
    
    # 分类和标签
    category = models.ForeignKey(
        DishCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dishes',
        verbose_name='分类'
    )
    tags = models.ManyToManyField(
        DishTag,
        blank=True,
        related_name='dishes',
        verbose_name='标签'
    )
    
    # 图片和媒体
    main_image = models.URLField(blank=True, verbose_name='主图')
    images = models.JSONField(default=list, verbose_name='图片列表')
    video_url = models.URLField(blank=True, verbose_name='视频链接')
    
    # 食材和配料
    ingredients = models.JSONField(default=list, verbose_name='食材列表')
    seasonings = models.JSONField(default=list, verbose_name='调料列表')
    tools = models.JSONField(default=list, verbose_name='厨具列表')
    
    # 烹饪步骤
    steps = models.JSONField(default=list, verbose_name='烹饪步骤')
    tips = models.TextField(blank=True, verbose_name='小贴士')
    
    # 营养信息
    calories = models.PositiveIntegerField(null=True, blank=True, verbose_name='卡路里')
    protein = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name='蛋白质(g)')
    carbs = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name='碳水化合物(g)')
    fat = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name='脂肪(g)')
    
    # 用户相关
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_dishes',
        verbose_name='创建者'
    )
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 评分和统计
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name='评分'
    )
    rating_count = models.PositiveIntegerField(default=0, verbose_name='评分次数')
    cooked_count = models.PositiveIntegerField(default=0, verbose_name='烹饪次数')
    view_count = models.PositiveIntegerField(default=0, verbose_name='查看次数')
    favorite_count = models.PositiveIntegerField(default=0, verbose_name='收藏次数')
    share_count = models.PositiveIntegerField(default=0, verbose_name='分享次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    last_cooked_at = models.DateTimeField(null=True, blank=True, verbose_name='最后烹饪时间')
    
    class Meta:
        db_table = 'dishes'
        verbose_name = '菜品'
        verbose_name_plural = '菜品'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['author']),
            models.Index(fields=['rating']),
            models.Index(fields=['cooked_count']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def update_rating(self, new_rating):
        """更新菜品评分"""
        total_rating = self.rating * self.rating_count + new_rating
        self.rating_count += 1
        self.rating = total_rating / self.rating_count
        self.save()
    
    def increment_cooked_count(self):
        """增加烹饪次数"""
        self.cooked_count += 1
        self.last_cooked_at = timezone.now()
        self.save()
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.save()
    
    def increment_favorite_count(self):
        """增加收藏次数"""
        self.favorite_count += 1
        self.save()
    
    def increment_share_count(self):
        """增加分享次数"""
        self.share_count += 1
        self.save()


class DishRating(models.Model):
    """菜品评分"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='菜品'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dish_ratings',
        verbose_name='用户'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='评分'
    )
    comment = models.TextField(blank=True, verbose_name='评论')
    is_anonymous = models.BooleanField(default=False, verbose_name='是否匿名')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'dish_ratings'
        verbose_name = '菜品评分'
        verbose_name_plural = '菜品评分'
        unique_together = ['dish', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.dish.name} - {self.user} - {self.rating}星'


class DishFavorite(models.Model):
    """菜品收藏"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='菜品'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_dishes',
        verbose_name='用户'
    )
    notes = models.TextField(blank=True, verbose_name='收藏备注')
    is_private = models.BooleanField(default=False, verbose_name='是否私有')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'dish_favorites'
        verbose_name = '菜品收藏'
        verbose_name_plural = '菜品收藏'
        unique_together = ['dish', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user} 收藏了 {self.dish.name}'


class DishCookingHistory(models.Model):
    """菜品烹饪历史"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='cooking_history',
        verbose_name='菜品'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cooked_dishes',
        verbose_name='用户'
    )
    
    # 烹饪信息
    cooking_date = models.DateField(verbose_name='烹饪日期')
    cooking_time = models.TimeField(verbose_name='烹饪时间')
    actual_cooking_time = models.PositiveIntegerField(null=True, blank=True, verbose_name='实际烹饪时间(分钟)')
    servings = models.PositiveSmallIntegerField(default=1, verbose_name='份量')
    notes = models.TextField(blank=True, verbose_name='烹饪笔记')
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='本次评分'
    )
    
    # 修改信息
    modifications = models.JSONField(default=dict, verbose_name='修改内容')
    success_level = models.CharField(
        max_length=20,
        choices=[
            ('perfect', '完美'),
            ('good', '良好'),
            ('ok', '一般'),
            ('failed', '失败')
        ],
        default='good',
        verbose_name='成功程度'
    )
    
    # 图片记录
    photos = models.JSONField(default=list, verbose_name='烹饪照片')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'dish_cooking_history'
        verbose_name = '菜品烹饪历史'
        verbose_name_plural = '菜品烹饪历史'
        ordering = ['-cooking_date', '-cooking_time']
        indexes = [
            models.Index(fields=['dish', 'user']),
            models.Index(fields=['cooking_date']),
        ]
    
    def __str__(self):
        return f'{self.user} 在 {self.cooking_date} 烹饪了 {self.dish.name}'


class DishComment(models.Model):
    """菜品评论"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='菜品'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dish_comments',
        verbose_name='用户'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='父评论'
    )
    
    # 评论内容
    content = models.TextField(verbose_name='评论内容')
    is_anonymous = models.BooleanField(default=False, verbose_name='是否匿名')
    is_edited = models.BooleanField(default=False, verbose_name='是否编辑过')
    
    # 互动统计
    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    reply_count = models.PositiveIntegerField(default=0, verbose_name='回复数')
    
    # 审核状态
    is_approved = models.BooleanField(default=True, verbose_name='是否审核通过')
    reported_count = models.PositiveIntegerField(default=0, verbose_name='举报次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'dish_comments'
        verbose_name = '菜品评论'
        verbose_name_plural = '菜品评论'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dish', 'parent']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.user} 评论了 {self.dish.name}'


class DishShare(models.Model):
    """菜品分享记录"""
    
    SHARE_PLATFORMS = [
        ('wechat', '微信'),
        ('wechat_moments', '朋友圈'),
        ('qq', 'QQ'),
        ('weibo', '微博'),
        ('copy_link', '复制链接'),
        ('other', '其他'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name='菜品'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dish_shares',
        verbose_name='用户'
    )
    
    # 分享信息
    platform = models.CharField(max_length=20, choices=SHARE_PLATFORMS, verbose_name='分享平台')
    share_method = models.CharField(max_length=50, blank=True, verbose_name='分享方式')
    share_content = models.TextField(blank=True, verbose_name='分享内容')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'dish_shares'
        verbose_name = '菜品分享'
        verbose_name_plural = '菜品分享'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dish', 'user']),
            models.Index(fields=['platform']),
        ]
    
    def __str__(self):
        return f'{self.user} 分享了 {self.dish.name} 到 {self.get_platform_display()}'