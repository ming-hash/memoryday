from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import os
from datetime import datetime

from .models import UploadedFile


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_file(request):
    """文件上传接口"""
    if 'file' not in request.FILES:
        return Response(
            {'error': '没有找到文件'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    user = request.user
    
    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return Response(
            {'error': '不支持的文件类型'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 验证文件大小 (最大5MB)
    max_size = 5 * 1024 * 1024
    if file.size > max_size:
        return Response(
            {'error': '文件大小不能超过5MB'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 生成唯一文件名
        file_ext = os.path.splitext(file.name)[1]
        filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # 保存文件
        relative_path = f"uploads/{filename}"
        file_path = default_storage.save(relative_path, ContentFile(file.read()))
        
        # 确定文件类型分类
        content_type = file.content_type
        if content_type.startswith('image/'):
            file_type = 'image'
        elif content_type.startswith('video/'):
            file_type = 'video'
        elif content_type.startswith('audio/'):
            file_type = 'audio'
        else:
            file_type = 'other'
        
        # 构建文件URL（返回相对路径，小程序端会自动补全为绝对URL）
        file_url = default_storage.url(file_path)
        
        # 创建上传记录
        uploaded_file = UploadedFile.objects.create(
            user=user,
            original_name=file.name,
            file_name=filename,
            file_type=file_type,
            file_size=file.size,
            mime_type=content_type,
            file_extension=file_ext.lstrip('.'),
            storage_path=file_path,
            storage_provider='local',
            storage_url=file_url,
            status='completed',
            metadata={
                'upload_type': request.data.get('upload_type', 'dish_image'),
                'original_content_type': file.content_type
            }
        )
        
        return Response({
            'id': uploaded_file.id,
            'original_name': uploaded_file.original_name,
            'file_name': uploaded_file.file_name,
            'file_url': file_url,
            'file_size': uploaded_file.file_size,
            'uploaded_at': uploaded_file.created_at
        })
        
    except Exception as e:
        return Response(
            {'error': f'文件上传失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_uploads(request):
    """获取用户上传文件列表"""
    user = request.user
    uploads = UploadedFile.objects.filter(user=user).order_by('-created_at')
    
    result = []
    for upload in uploads:
        file_url = upload.storage_url or default_storage.url(upload.storage_path)
        result.append({
            'id': upload.id,
            'original_name': upload.original_name,
            'file_name': upload.file_name,
            'file_url': file_url,
            'file_size': upload.file_size,
            'mime_type': upload.mime_type,
            'file_type': upload.file_type,
            'upload_type': upload.metadata.get('upload_type', '') if upload.metadata else '',
            'uploaded_at': upload.created_at
        })
    
    return Response({'uploads': result})


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_upload(request, file_id):
    """删除上传文件"""
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id, user=request.user)
        
        # 删除物理文件
        if default_storage.exists(uploaded_file.storage_path):
            default_storage.delete(uploaded_file.storage_path)
        
        # 删除数据库记录
        uploaded_file.delete()
        
        return Response({'message': '文件删除成功'})
        
    except UploadedFile.DoesNotExist:
        return Response(
            {'error': '文件不存在或无权访问'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'文件删除失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """健康检查接口"""
    return Response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'upload-service'
    })