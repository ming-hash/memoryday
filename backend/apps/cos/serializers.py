"""
COS应用序列化器
"""
from rest_framework import serializers
from .models import CosFile


class CosFileSerializer(serializers.ModelSerializer):
    """COS文件记录序列化器"""
    
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    upload_type_display = serializers.CharField(source='get_upload_type_display', read_only=True)
    
    class Meta:
        model = CosFile
        fields = [
            'id', 'user', 'file_key', 'original_name', 'file_size', 
            'content_type', 'upload_type', 'upload_type_display',
            'bucket', 'region', 'created_at', 'updated_at',
            'file_url', 'thumbnail_url', 'preview_url'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_file_url(self, obj):
        """获取文件URL"""
        return obj.file_url
    
    def get_thumbnail_url(self, obj):
        """获取缩略图URL"""
        return obj.thumbnail_url
    
    def get_preview_url(self, obj):
        """获取预览图URL"""
        return obj.preview_url


class CosFileCreateSerializer(serializers.ModelSerializer):
    """COS文件创建序列化器"""
    
    class Meta:
        model = CosFile
        fields = ['file_key', 'original_name', 'file_size', 'content_type', 'upload_type', 'bucket', 'region']
    
    def create(self, validated_data):
        """创建文件记录"""
        # 获取当前用户
        user = self.context['request'].user
        validated_data['user'] = user
        
        return super().create(validated_data)


class CosUploadRequestSerializer(serializers.Serializer):
    """文件上传请求序列化器"""
    
    folder = serializers.CharField(default='images', help_text='上传文件夹')
    upload_type = serializers.ChoiceField(
        choices=CosFile.UPLOAD_TYPE_CHOICES,
        default='dish_image',
        help_text='上传类型'
    )
    filename = serializers.CharField(required=False, help_text='自定义文件名')


class CosUploadResponseSerializer(serializers.Serializer):
    """文件上传响应序列化器"""
    
    success = serializers.BooleanField(help_text='是否成功')
    key = serializers.CharField(help_text='文件Key')
    url = serializers.CharField(help_text='文件URL')
    filename = serializers.CharField(help_text='文件名')
    size = serializers.IntegerField(help_text='文件大小')
    etag = serializers.CharField(help_text='文件ETag')
    uploaded_at = serializers.CharField(help_text='上传时间')


class CosDeleteResponseSerializer(serializers.Serializer):
    """文件删除响应序列化器"""
    
    success = serializers.BooleanField(help_text='是否成功')
    message = serializers.CharField(help_text='消息')
    key = serializers.CharField(help_text='文件Key')


class CosStsTokenSerializer(serializers.Serializer):
    """STS临时凭证序列化器"""
    
    tmpSecretId = serializers.CharField(help_text='临时SecretId')
    tmpSecretKey = serializers.CharField(help_text='临时SecretKey')
    sessionToken = serializers.CharField(help_text='会话Token')
    expiredTime = serializers.IntegerField(help_text='过期时间')
    startTime = serializers.IntegerField(help_text='开始时间')
    requestId = serializers.CharField(help_text='请求ID')


class CosFileInfoSerializer(serializers.Serializer):
    """文件信息序列化器"""
    
    key = serializers.CharField(help_text='文件Key')
    size = serializers.IntegerField(help_text='文件大小')
    last_modified = serializers.CharField(help_text='最后修改时间')
    etag = serializers.CharField(help_text='文件ETag')
    url = serializers.CharField(help_text='文件URL')


class CosListResponseSerializer(serializers.Serializer):
    """文件列表响应序列化器"""
    
    files = CosFileInfoSerializer(many=True, help_text='文件列表')
    total = serializers.IntegerField(help_text='文件总数')