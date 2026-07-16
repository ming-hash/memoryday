from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from apps.users.models import User
from apps.dishes.models import Dish


class DailyStat(models.Model):
    """每日统计"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True, verbose_name='统计日期')
    
    # 用户统计
    new_users = models.PositiveIntegerField(default=0, verbose_name='新增用户')
    active_users = models.PositiveIntegerField(default=0, verbose_name='活跃用户')
    total_users = models.PositiveIntegerField(default=0, verbose_name='总用户数')
    
    # 菜品统计
    new_dishes = models.PositiveIntegerField(default=0, verbose_name='新增菜品')
    cooked_dishes = models.PositiveIntegerField(default=0, verbose_name='烹饪菜品')
    total_dishes = models.PositiveIntegerField(default=0, verbose_name='总菜品数')
    
    # 互动统计
    dish_views = models.PositiveIntegerField(default=0, verbose_name='菜品查看次数')
    dish_ratings = models.PositiveIntegerField(default=0, verbose_name='菜品评分次数')
    dish_favorites = models.PositiveIntegerField(default=0, verbose_name='菜品收藏次数')
    dish_shares = models.PositiveIntegerField(default=0, verbose_name='菜品分享次数')
    comments = models.PositiveIntegerField(default=0, verbose_name='评论次数')
    
    # 时间统计
    total_cooking_time = models.PositiveIntegerField(default=0, verbose_name='总烹饪时间(分钟)')
    avg_cooking_time = models.DecimalField(max_digits=5, decimal_places=1, default=0.0, verbose_name='平均烹饪时间')
    
    # 平台统计
    app_launches = models.PositiveIntegerField(default=0, verbose_name='应用启动次数')
    api_calls = models.PositiveIntegerField(default=0, verbose_name='API调用次数')
    error_count = models.PositiveIntegerField(default=0, verbose_name='错误次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'daily_stats'
        verbose_name = '每日统计'
        verbose_name_plural = '每日统计'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f'统计: {self.date}'


class UserStat(models.Model):
    """用户统计"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='stats',
        verbose_name='用户'
    )
    
    # 活动统计
    total_dishes_created = models.PositiveIntegerField(default=0, verbose_name='创建菜品总数')
    total_dishes_cooked = models.PositiveIntegerField(default=0, verbose_name='烹饪菜品总数')
    total_cooking_time = models.PositiveIntegerField(default=0, verbose_name='总烹饪时间(分钟)')
    avg_cooking_time = models.DecimalField(max_digits=5, decimal_places=1, default=0.0, verbose_name='平均烹饪时间')
    
    # 互动统计
    total_ratings_given = models.PositiveIntegerField(default=0, verbose_name='评分次数')
    total_favorites = models.PositiveIntegerField(default=0, verbose_name='收藏次数')
    total_shares = models.PositiveIntegerField(default=0, verbose_name='分享次数')
    total_comments = models.PositiveIntegerField(default=0, verbose_name='评论次数')
    
    # 成就统计
    consecutive_login_days = models.PositiveIntegerField(default=0, verbose_name='连续登录天数')
    longest_streak = models.PositiveIntegerField(default=0, verbose_name='最长连续记录')
    achievement_score = models.PositiveIntegerField(default=0, verbose_name='成就分数')
    
    # 时间统计
    first_activity_date = models.DateField(null=True, blank=True, verbose_name='首次活动日期')
    last_activity_date = models.DateField(null=True, blank=True, verbose_name='最后活动日期')
    total_active_days = models.PositiveIntegerField(default=0, verbose_name='活跃天数')
    
    # 偏好统计
    favorite_cuisine = models.CharField(max_length=50, blank=True, verbose_name='最喜爱菜系')
    favorite_cooking_method = models.CharField(max_length=50, blank=True, verbose_name='最喜爱烹饪方法')
    most_used_ingredients = models.JSONField(default=list, verbose_name='最常用食材')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'user_stats'
        verbose_name = '用户统计'
        verbose_name_plural = '用户统计'
        ordering = ['-achievement_score']
    
    def __str__(self):
        return f'{self.user} 的统计'


class DishStat(models.Model):
    """菜品统计"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dish = models.OneToOneField(
        Dish,
        on_delete=models.CASCADE,
        related_name='stats',
        verbose_name='菜品'
    )
    
    # 基础统计
    view_count = models.PositiveIntegerField(default=0, verbose_name='查看次数')
    cooked_count = models.PositiveIntegerField(default=0, verbose_name='烹饪次数')
    favorite_count = models.PositiveIntegerField(default=0, verbose_name='收藏次数')
    share_count = models.PositiveIntegerField(default=0, verbose_name='分享次数')
    comment_count = models.PositiveIntegerField(default=0, verbose_name='评论次数')
    
    # 评分统计
    rating_count = models.PositiveIntegerField(default=0, verbose_name='评分次数')
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        verbose_name='平均评分'
    )
    rating_distribution = models.JSONField(default=dict, verbose_name='评分分布')
    
    # 时间统计
    first_cooked_date = models.DateField(null=True, blank=True, verbose_name='首次烹饪日期')
    last_cooked_date = models.DateField(null=True, blank=True, verbose_name='最后烹饪日期')
    avg_cooking_time = models.DecimalField(max_digits=5, decimal_places=1, default=0.0, verbose_name='平均烹饪时间')
    
    # 用户统计
    unique_cooks = models.PositiveIntegerField(default=0, verbose_name='独特烹饪用户数')
    user_success_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='用户成功率'
    )
    
    # 流行度指标
    popularity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='流行度分数'
    )
    trend_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='趋势分数'
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'dish_stats'
        verbose_name = '菜品统计'
        verbose_name_plural = '菜品统计'
        ordering = ['-popularity_score']
    
    def __str__(self):
        return f'{self.dish.name} 的统计'


class CookingSession(models.Model):
    """烹饪会话统计"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cooking_sessions',
        verbose_name='用户'
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='cooking_sessions',
        verbose_name='菜品'
    )
    
    # 会话信息
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration = models.PositiveIntegerField(null=True, blank=True, verbose_name='持续时间(秒)')
    
    # 烹饪结果
    success_level = models.CharField(
        max_length=20,
        choices=[
            ('perfect', '完美'),
            ('good', '良好'),
            ('ok', '一般'),
            ('failed', '失败')
        ],
        verbose_name='成功程度'
    )
    user_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='用户评分'
    )
    
    # 修改信息
    modifications = models.JSONField(default=dict, verbose_name='修改内容')
    ingredients_used = models.JSONField(default=list, verbose_name='使用食材')
    tools_used = models.JSONField(default=list, verbose_name='使用工具')
    
    # 环境信息
    device_info = models.JSONField(default=dict, verbose_name='设备信息')
    location = models.CharField(max_length=100, blank=True, verbose_name='位置')
    weather = models.CharField(max_length=50, blank=True, verbose_name='天气')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'cooking_sessions'
        verbose_name = '烹饪会话'
        verbose_name_plural = '烹饪会话'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', 'dish']),
            models.Index(fields=['start_time']),
        ]
    
    def __str__(self):
        return f'{self.user} 烹饪 {self.dish.name} - {self.start_time}'


class AppUsageStat(models.Model):
    """应用使用统计"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='app_usage_stats',
        verbose_name='用户'
    )
    
    # 使用信息
    session_start = models.DateTimeField(verbose_name='会话开始时间')
    session_end = models.DateTimeField(null=True, blank=True, verbose_name='会话结束时间')
    session_duration = models.PositiveIntegerField(default=0, verbose_name='会话时长(秒)')
    
    # 功能使用
    pages_visited = models.JSONField(default=list, verbose_name='访问页面')
    features_used = models.JSONField(default=list, verbose_name='使用功能')
    searches_performed = models.PositiveIntegerField(default=0, verbose_name='搜索次数')
    notifications_received = models.PositiveIntegerField(default=0, verbose_name='通知接收数')
    
    # 性能指标
    app_load_time = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name='应用加载时间')
    api_response_time = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name='API响应时间')
    error_count = models.PositiveIntegerField(default=0, verbose_name='错误次数')
    
    # 设备信息
    device_type = models.CharField(max_length=50, blank=True, verbose_name='设备类型')
    os_version = models.CharField(max_length=20, blank=True, verbose_name='系统版本')
    app_version = models.CharField(max_length=20, blank=True, verbose_name='应用版本')
    network_type = models.CharField(max_length=20, blank=True, verbose_name='网络类型')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'app_usage_stats'
        verbose_name = '应用使用统计'
        verbose_name_plural = '应用使用统计'
        ordering = ['-session_start']
        indexes = [
            models.Index(fields=['user', 'session_start']),
        ]
    
    def __str__(self):
        return f'{self.user} 的应用使用 - {self.session_start}'


class Achievement(models.Model):
    """成就系统"""
    
    ACHIEVEMENT_TYPES = [
        ('cooking', '烹饪'),
        ('creation', '创作'),
        ('exploration', '探索'),
        ('social', '社交'),
        ('consistency', '坚持'),
        ('mastery', '精通'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='成就名称')
    description = models.TextField(verbose_name='成就描述')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES, verbose_name='成就类型')
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标')
    color = models.CharField(max_length=20, blank=True, verbose_name='颜色')
    
    # 达成条件
    condition_type = models.CharField(max_length=50, verbose_name='条件类型')
    condition_value = models.PositiveIntegerField(verbose_name='条件值')
    condition_data = models.JSONField(default=dict, verbose_name='条件数据')
    
    # 奖励信息
    points = models.PositiveIntegerField(default=0, verbose_name='奖励积分')
    badge = models.CharField(max_length=50, blank=True, verbose_name='徽章')
    unlock_message = models.TextField(blank=True, verbose_name='解锁消息')
    
    # 统计信息
    unlocked_count = models.PositiveIntegerField(default=0, verbose_name='解锁人数')
    rarity = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='稀有度'
    )
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_hidden = models.BooleanField(default=False, verbose_name='是否隐藏')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'achievements'
        verbose_name = '成就'
        verbose_name_plural = '成就'
        ordering = ['achievement_type', 'points']
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """用户成就"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='用户'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name='成就'
    )
    
    # 达成信息
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name='解锁时间')
    progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='进度'
    )
    current_value = models.PositiveIntegerField(default=0, verbose_name='当前值')
    is_unlocked = models.BooleanField(default=False, verbose_name='是否已解锁')
    
    # 分享信息
    shared_at = models.DateTimeField(null=True, blank=True, verbose_name='分享时间')
    share_count = models.PositiveIntegerField(default=0, verbose_name='分享次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'user_achievements'
        verbose_name = '用户成就'
        verbose_name_plural = '用户成就'
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']
    
    def __str__(self):
        status = "已解锁" if self.is_unlocked else "进行中"
        return f'{self.user} - {self.achievement.name} ({status})'