from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from apps.users.models import User


class UploadedFile(models.Model):
    """上传文件模型"""
    
    FILE_TYPES = [
        ('image', '图片'),
        ('video', '视频'),
        ('audio', '音频'),
        ('document', '文档'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('deleted', '已删除'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        verbose_name='用户'
    )
    
    # 文件信息
    original_name = models.CharField(max_length=255, verbose_name='原始文件名')
    file_name = models.CharField(max_length=255, unique=True, verbose_name='存储文件名')
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, verbose_name='文件类型')
    file_size = models.PositiveBigIntegerField(verbose_name='文件大小(字节)')
    mime_type = models.CharField(max_length=100, verbose_name='MIME类型')
    file_extension = models.CharField(max_length=20, verbose_name='文件扩展名')
    
    # 存储信息
    storage_path = models.CharField(max_length=500, verbose_name='存储路径')
    storage_provider = models.CharField(max_length=50, default='local', verbose_name='存储提供商')
    storage_url = models.URLField(blank=True, verbose_name='存储URL')
    cdn_url = models.URLField(blank=True, verbose_name='CDN URL')
    
    # 处理信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    processing_data = models.JSONField(default=dict, verbose_name='处理数据')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    retry_count = models.PositiveIntegerField(default=0, verbose_name='重试次数')
    
    # 元数据
    metadata = models.JSONField(default=dict, verbose_name='元数据')
    tags = models.JSONField(default=list, verbose_name='标签')
    
    # 安全信息
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    access_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='访问密钥')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='处理完成时间')
    
    class Meta:
        db_table = 'uploaded_files'
        verbose_name = '上传文件'
        verbose_name_plural = '上传文件'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'file_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.original_name} ({self.file_type})'
    
    @property
    def file_url(self):
        """获取文件URL"""
        return self.cdn_url or self.storage_url
    
    @property
    def human_file_size(self):
        """获取人类可读的文件大小"""
        if self.file_size == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        size = self.file_size
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        return f"{size:.2f}{size_names[i]}"
    
    def mark_as_processing(self):
        """标记为处理中"""
        self.status = 'processing'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_completed(self, data=None):
        """标记为完成"""
        self.status = 'completed'
        self.processed_at = timezone.now()
        if data:
            self.processing_data = data
        self.save(update_fields=['status', 'processed_at', 'processing_data', 'updated_at'])
    
    def mark_as_failed(self, error_message):
        """标记为失败"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save(update_fields=['status', 'error_message', 'retry_count', 'updated_at'])


class ImageProcessingJob(models.Model):
    """图片处理任务"""
    
    JOB_TYPES = [
        ('resize', '调整大小'),
        ('crop', '裁剪'),
        ('compress', '压缩'),
        ('watermark', '添加水印'),
        ('format_convert', '格式转换'),
        ('optimize', '优化'),
        ('multiple', '多操作'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name='processing_jobs',
        verbose_name='上传文件'
    )
    
    # 任务信息
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, verbose_name='任务类型')
    parameters = models.JSONField(default=dict, verbose_name='处理参数')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    
    # 结果信息
    result_file = models.ForeignKey(
        UploadedFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_from',
        verbose_name='结果文件'
    )
    processing_data = models.JSONField(default=dict, verbose_name='处理数据')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    # 性能指标
    processing_time = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name='处理时间(秒)')
    memory_usage = models.PositiveIntegerField(null=True, blank=True, verbose_name='内存使用(字节)')
    quality_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name='质量评分'
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        db_table = 'image_processing_jobs'
        verbose_name = '图片处理任务'
        verbose_name_plural = '图片处理任务'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploaded_file', 'job_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'{self.uploaded_file.original_name} - {self.get_job_type_display()}'
    
    def mark_as_processing(self):
        """标记为处理中"""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])
    
    def mark_as_completed(self, result_file=None, data=None):
        """标记为完成"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if result_file:
            self.result_file = result_file
        if data:
            self.processing_data = data
        self.processing_time = (self.completed_at - self.started_at).total_seconds()
        self.save(update_fields=[
            'status', 'completed_at', 'result_file', 'processing_data', 
            'processing_time', 'updated_at'
        ])
    
    def mark_as_failed(self, error_message):
        """标记为失败"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        if self.started_at:
            self.processing_time = (self.completed_at - self.started_at).total_seconds()
        self.save(update_fields=[
            'status', 'completed_at', 'error_message', 'processing_time', 'updated_at'
        ])


class FileAccessLog(models.Model):
    """文件访问日志"""
    
    ACCESS_TYPES = [
        ('read', '读取'),
        ('download', '下载'),
        ('preview', '预览'),
        ('share', '分享'),
        ('delete', '删除'),
        ('update', '更新'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name='access_logs',
        verbose_name='文件'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='file_access_logs',
        verbose_name='用户'
    )
    
    # 访问信息
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES, verbose_name='访问类型')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    referrer = models.URLField(blank=True, verbose_name='来源URL')
    
    # 访问结果
    success = models.BooleanField(default=True, verbose_name='是否成功')
    status_code = models.PositiveSmallIntegerField(default=200, verbose_name='状态码')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    bytes_transferred = models.PositiveBigIntegerField(null=True, blank=True, verbose_name='传输字节数')
    
    # 性能指标
    response_time = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name='响应时间(秒)')
    cache_status = models.CharField(max_length=20, blank=True, verbose_name='缓存状态')
    
    # 时间戳
    accessed_at = models.DateTimeField(auto_now_add=True, verbose_name='访问时间')
    
    class Meta:
        db_table = 'file_access_logs'
        verbose_name = '文件访问日志'
        verbose_name_plural = '文件访问日志'
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['uploaded_file', 'access_type']),
            models.Index(fields=['user', 'accessed_at']),
            models.Index(fields=['ip_address', 'accessed_at']),
        ]
    
    def __str__(self):
        return f'{self.uploaded_file} - {self.get_access_type_display()} - {self.accessed_at}'


class StorageQuota(models.Model):
    """存储配额"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='storage_quota',
        verbose_name='用户'
    )
    
    # 配额限制
    max_storage_bytes = models.PositiveBigIntegerField(default=10737418240, verbose_name='最大存储空间(字节)')  # 10GB
    max_file_size = models.PositiveBigIntegerField(default=104857600, verbose_name='最大文件大小(字节)')  # 100MB
    max_files_per_day = models.PositiveIntegerField(default=100, verbose_name='每日最大文件数')
    
    # 使用情况
    used_storage_bytes = models.PositiveBigIntegerField(default=0, verbose_name='已用存储空间(字节)')
    files_uploaded_today = models.PositiveIntegerField(default=0, verbose_name='今日已上传文件数')
    total_files = models.PositiveIntegerField(default=0, verbose_name='总文件数')
    
    # 时间信息
    last_reset_date = models.DateField(default=timezone.now, verbose_name='最后重置日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'storage_quotas'
        verbose_name = '存储配额'
        verbose_name_plural = '存储配额'
    
    def __str__(self):
        return f'{self.user} 的存储配额'
    
    @property
    def used_storage_percentage(self):
        """已用存储百分比"""
        if self.max_storage_bytes == 0:
            return 0
        return (self.used_storage_bytes / self.max_storage_bytes) * 100
    
    @property
    def remaining_storage_bytes(self):
        """剩余存储空间"""
        return max(0, self.max_storage_bytes - self.used_storage_bytes)
    
    @property
    def can_upload_file(self, file_size=0):
        """检查是否可以上传文件"""
        if timezone.now().date() > self.last_reset_date:
            self.reset_daily_quota()
        
        return (
            self.used_storage_bytes + file_size <= self.max_storage_bytes and
            self.files_uploaded_today < self.max_files_per_day and
            file_size <= self.max_file_size
        )
    
    def reset_daily_quota(self):
        """重置每日配额"""
        self.files_uploaded_today = 0
        self.last_reset_date = timezone.now().date()
        self.save(update_fields=['files_uploaded_today', 'last_reset_date', 'updated_at'])
    
    def update_usage(self, file_size, increment=True):
        """更新使用情况"""
        if increment:
            self.used_storage_bytes += file_size
            self.files_uploaded_today += 1
            self.total_files += 1
        else:
            self.used_storage_bytes = max(0, self.used_storage_bytes - file_size)
            self.total_files = max(0, self.total_files - 1)
        
        self.save(update_fields=[
            'used_storage_bytes', 'files_uploaded_today', 'total_files', 'updated_at'
        ])


class FileShareLink(models.Model):
    """文件分享链接"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name='share_links',
        verbose_name='文件'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_share_links',
        verbose_name='创建者'
    )
    
    # 分享信息
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='分享令牌')
    password = models.CharField(max_length=100, blank=True, verbose_name='访问密码')
    description = models.TextField(blank=True, verbose_name='分享描述')
    
    # 访问限制
    max_views = models.PositiveIntegerField(default=0, verbose_name='最大查看次数')  # 0表示无限制
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')
    require_password = models.BooleanField(default=False, verbose_name='需要密码')
    allow_download = models.BooleanField(default=True, verbose_name='允许下载')
    allow_preview = models.BooleanField(default=True, verbose_name='允许预览')
    
    # 统计信息
    view_count = models.PositiveIntegerField(default=0, verbose_name='查看次数')
    download_count = models.PositiveIntegerField(default=0, verbose_name='下载次数')
    last_accessed_at = models.DateTimeField(null=True, blank=True, verbose_name='最后访问时间')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'file_share_links'
        verbose_name = '文件分享链接'
        verbose_name_plural = '文件分享链接'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['share_token']),
            models.Index(fields=['uploaded_file', 'created_by']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f'{self.uploaded_file} 的分享链接'
    
    @property
    def share_url(self):
        """获取分享URL"""
        return f"/share/{self.share_token}/"
    
    @property
    def is_expired(self):
        """检查是否过期"""
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        if self.max_views > 0 and self.view_count >= self.max_views:
            return True
        return False
    
    @property
    def is_active(self):
        """检查是否有效"""
        return not self.is_expired and self.uploaded_file.status == 'completed'
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.last_accessed_at = timezone.now()
        self.save(update_fields=['view_count', 'last_accessed_at', 'updated_at'])
    
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        self.last_accessed_at = timezone.now()
        self.save(update_fields=['download_count', 'last_accessed_at', 'updated_at'])