from django.db import models
from django.conf import settings


class CosFile(models.Model):
    """
    COS文件记录模型
    记录用户上传到COS的文件信息
    """
    UPLOAD_TYPE_CHOICES = [
        ('dish_image', '菜品图片'),
        ('user_avatar', '用户头像'),
        ('other', '其他文件'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='上传用户')
    file_key = models.CharField(max_length=500, verbose_name='COS文件Key')
    original_name = models.CharField(max_length=255, verbose_name='原始文件名')
    file_size = models.BigIntegerField(verbose_name='文件大小（字节）')
    content_type = models.CharField(max_length=100, verbose_name='文件类型')
    upload_type = models.CharField(
        max_length=20, 
        choices=UPLOAD_TYPE_CHOICES, 
        default='dish_image',
        verbose_name='上传类型'
    )
    
    # 文件URL（动态生成，不存储）
    bucket = models.CharField(max_length=255, verbose_name='存储桶名称')
    region = models.CharField(max_length=50, verbose_name='存储桶地域')
    
    # 元数据
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'cos_files'
        verbose_name = 'COS文件记录'
        verbose_name_plural = 'COS文件记录'
        indexes = [
            models.Index(fields=['user', 'upload_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.original_name} ({self.file_key})"
    
    @property
    def file_url(self):
        """动态生成文件URL"""
        return f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{self.file_key}"
    
    @property
    def thumbnail_url(self):
        """生成缩略图URL"""
        return f"{self.file_url}?imageView2/1/w/200/h/200"
    
    @property
    def preview_url(self):
        """生成预览图URL"""
        return f"{self.file_url}?imageView2/0/q/80"
    
    def get_file_info(self):
        """获取文件信息"""
        return {
            'id': self.id,
            'key': self.file_key,
            'original_name': self.original_name,
            'url': self.file_url,
            'thumbnail_url': self.thumbnail_url,
            'preview_url': self.preview_url,
            'size': self.file_size,
            'content_type': self.content_type,
            'upload_type': self.upload_type,
            'uploaded_at': self.created_at.isoformat(),
            'user_id': self.user_id
        }