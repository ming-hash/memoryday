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
        file_path = default_storage.save(f"uploads/{filename}", ContentFile(file.read()))
        
        # 创建上传记录
        uploaded_file = UploadedFile.objects.create(
            user=user,
            original_name=file.name,
            file_name=filename,
            file_path=file_path,
            file_size=file.size,
            content_type=file.content_type,
            upload_type=request.data.get('upload_type', 'dish_image')
        )
        
        # 构建文件URL
        file_url = default_storage.url(file_path)
        
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
        result.append({
            'id': upload.id,
            'original_name': upload.original_name,
            'file_name': upload.file_name,
            'file_url': default_storage.url(upload.file_path),
            'file_size': upload.file_size,
            'content_type': upload.content_type,
            'upload_type': upload.upload_type,
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
        if default_storage.exists(uploaded_file.file_path):
            default_storage.delete(uploaded_file.file_path)
        
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