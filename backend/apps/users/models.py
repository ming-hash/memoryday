from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """自定义用户管理器"""
    
    def create_user(self, phone, password=None, **extra_fields):
        """创建普通用户"""
        if not phone:
            raise ValueError('手机号是必填项')
        
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置is_superuser=True')
            
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """自定义用户模型"""
    
    # 手机号验证器
    phone_validator = RegexValidator(
        regex=r'^1[3-9]\d{9}$',
        message='请输入有效的手机号码'
    )
    
    # 基本信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name='手机号'
    )
    nickname = models.CharField(max_length=50, blank=True, verbose_name='昵称')
    avatar = models.URLField(blank=True, verbose_name='头像')
    gender = models.CharField(
        max_length=10,
        choices=[('male', '男'), ('female', '女'), ('unknown', '未知')],
        default='unknown',
        verbose_name='性别'
    )
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    
    # 微信相关字段
    openid = models.CharField(max_length=100, null=True, blank=True, unique=True, verbose_name='微信OpenID')
    unionid = models.CharField(max_length=100, null=True, blank=True, unique=True, verbose_name='微信UnionID')
    wechat_info = models.JSONField(default=dict, verbose_name='微信用户信息')
    
    # 权限相关
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_staff = models.BooleanField(default=False, verbose_name='是否员工')
    is_superuser = models.BooleanField(default=False, verbose_name='是否超级用户')
    
    # 时间戳
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='注册时间')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='最后登录')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 饮食偏好
    dietary_preferences = models.JSONField(default=dict, verbose_name='饮食偏好')
    allergies = models.JSONField(default=list, verbose_name='过敏食物')
    disliked_foods = models.JSONField(default=list, verbose_name='不喜欢的食物')
    
    # 统计信息
    total_dishes_created = models.PositiveIntegerField(default=0, verbose_name='创建菜品数')
    total_dishes_cooked = models.PositiveIntegerField(default=0, verbose_name='烹饪菜品数')
    
    # 设置字段
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f'{self.nickname or self.phone}'
    
    @property
    def is_wechat_user(self):
        """是否是微信用户"""
        return bool(self.openid)
    
    def get_full_name(self):
        return self.nickname or self.phone
    
    def get_short_name(self):
        return self.nickname or self.phone
    
    def update_login_time(self):
        """更新最后登录时间"""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])


class UserProfile(models.Model):
    """用户扩展资料"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户'
    )
    
    # 个人信息
    bio = models.TextField(blank=True, verbose_name='个人简介')
    location = models.CharField(max_length=100, blank=True, verbose_name='所在地')
    cooking_experience = models.CharField(
        max_length=20,
        choices=[
            ('beginner', '新手'),
            ('intermediate', '中级'),
            ('advanced', '高级'),
            ('expert', '专家')
        ],
        default='beginner',
        verbose_name='烹饪经验'
    )
    
    # 偏好设置
    preferred_cuisines = models.JSONField(default=list, verbose_name='偏好菜系')
    preferred_cooking_time = models.CharField(
        max_length=20,
        choices=[
            ('quick', '快速（15分钟内）'),
            ('medium', '中等（15-30分钟）'),
            ('long', '较慢（30-60分钟）'),
            ('very_long', '慢炖（60分钟以上）')
        ],
        default='medium',
        verbose_name='偏好烹饪时间'
    )
    
    # 通知设置
    enable_notifications = models.BooleanField(default=True, verbose_name='启用通知')
    enable_meal_reminders = models.BooleanField(default=True, verbose_name='用餐提醒')
    enable_new_dish_notifications = models.BooleanField(default=True, verbose_name='新菜品通知')
    
    # 隐私设置
    show_profile_public = models.BooleanField(default=True, verbose_name='公开个人资料')
    show_cooked_dishes = models.BooleanField(default=True, verbose_name='显示烹饪记录')
    show_created_dishes = models.BooleanField(default=True, verbose_name='显示创建菜品')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return f'{self.user} 的资料'


class UserActivity(models.Model):
    """用户活动记录"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name='用户'
    )
    
    ACTIVITY_TYPES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('create_dish', '创建菜品'),
        ('update_dish', '更新菜品'),
        ('delete_dish', '删除菜品'),
        ('cook_dish', '烹饪菜品'),
        ('view_dish', '查看菜品'),
        ('search', '搜索'),
        ('share', '分享'),
        ('rate', '评分'),
        ('comment', '评论'),
    ]
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, verbose_name='活动类型')
    target_id = models.UUIDField(null=True, blank=True, verbose_name='目标ID')
    target_type = models.CharField(max_length=50, blank=True, verbose_name='目标类型')
    description = models.TextField(blank=True, verbose_name='活动描述')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = '用户活动'
        verbose_name_plural = '用户活动'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.user} - {self.get_activity_type_display()} - {self.created_at}'


class LoginHistory(models.Model):
    """登录历史记录"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history',
        verbose_name='用户'
    )
    
    login_method = models.CharField(
        max_length=20,
        choices=[
            ('phone', '手机号登录'),
            ('wechat', '微信登录'),
            ('token', 'Token登录')
        ],
        verbose_name='登录方式'
    )
    
    # 设备信息
    device_type = models.CharField(max_length=50, blank=True, verbose_name='设备类型')
    device_id = models.CharField(max_length=100, blank=True, verbose_name='设备ID')
    app_version = models.CharField(max_length=20, blank=True, verbose_name='应用版本')
    os_version = models.CharField(max_length=20, blank=True, verbose_name='系统版本')
    
    # 网络信息
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    network_type = models.CharField(max_length=20, blank=True, verbose_name='网络类型')
    location = models.CharField(max_length=100, blank=True, verbose_name='登录地点')
    
    # 登录结果
    success = models.BooleanField(default=True, verbose_name='是否成功')
    failure_reason = models.CharField(max_length=200, blank=True, verbose_name='失败原因')
    
    # 时间戳
    login_time = models.DateTimeField(auto_now_add=True, verbose_name='登录时间')
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name='登出时间')
    session_duration = models.DurationField(null=True, blank=True, verbose_name='会话时长')
    
    class Meta:
        db_table = 'login_history'
        verbose_name = '登录历史'
        verbose_name_plural = '登录历史'
        ordering = ['-login_time']
    
    def __str__(self):
        status = '成功' if self.success else '失败'
        return f'{self.user} - {self.login_method} - {status} - {self.login_time}'