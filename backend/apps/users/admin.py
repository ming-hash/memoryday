from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, UserActivity, LoginHistory


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理界面"""
    
    list_display = ('phone', 'nickname', 'is_active', 'is_staff', 'date_joined', 'last_login')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'gender', 'date_joined')
    search_fields = ('phone', 'nickname', 'openid', 'unionid')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('个人信息', {'fields': ('nickname', 'avatar', 'gender', 'birthday')}),
        ('微信信息', {'fields': ('openid', 'unionid', 'wechat_info')}),
        ('饮食偏好', {'fields': ('dietary_preferences', 'allergies', 'disliked_foods')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('统计信息', {'fields': ('total_dishes_created', 'total_dishes_cooked')}),
        ('时间信息', {'fields': ('date_joined', 'last_login', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2', 'nickname'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户资料管理"""
    
    list_display = ('user', 'cooking_experience', 'location', 'created_at')
    list_filter = ('cooking_experience', 'enable_notifications', 'show_profile_public')
    search_fields = ('user__phone', 'user__nickname', 'location')
    raw_id_fields = ('user',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """用户活动管理"""
    
    list_display = ('user', 'activity_type', 'target_type', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__phone', 'user__nickname', 'description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """登录历史管理"""
    
    list_display = ('user', 'login_method', 'success', 'login_time', 'device_type')
    list_filter = ('login_method', 'success', 'login_time', 'network_type')
    search_fields = ('user__phone', 'user__nickname', 'ip_address', 'device_id')
    readonly_fields = ('login_time', 'logout_time', 'session_duration')
    date_hierarchy = 'login_time'