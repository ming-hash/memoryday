from rest_framework import permissions, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
import boto3
from botocore.exceptions import ClientError
import uuid
import json
from datetime import datetime, timedelta
import logging

from .models import CosFile
from .serializers import (
    CosFileSerializer, CosFileCreateSerializer, 
    CosUploadRequestSerializer, CosUploadResponseSerializer,
    CosDeleteResponseSerializer, CosStsTokenSerializer,
    CosListResponseSerializer, CosFileInfoSerializer
)
from .services import cos_service

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def get_sts_token(request):
    """
    获取腾讯云COS STS临时凭证
    小程序前端通过此接口获取临时密钥进行文件上传
    """
    try:
        # 检查COS服务是否启用
        if not cos_service.is_enabled():
            return Response(
                {'error': 'COS服务未启用'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 获取配置
        config = cos_service.config
        secret_id = config.get('secret_id')
        secret_key = config.get('secret_key')
        bucket = config.get('bucket')
        region = config.get('region')
        app_id = config.get('app_id')
        
        if not all([secret_id, secret_key, bucket, region]):
            return Response(
                {'error': 'COS配置不完整'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 使用boto3获取临时凭证
        client = boto3.client(
            'sts',
            aws_access_key_id=secret_id,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # 构建COS的resource
        resource = f"qcs::cos:{region}:uid/{app_id}:{bucket}/*"
        
        # 获取临时凭证
        response = client.assume_role(
            RoleArn=f"qcs::cam::uids/{app_id}:rolename/COSUploadRole",
            RoleSessionName='cos-upload-session',
            DurationSeconds=1800,
            Policy=json.dumps({
                'version': '2.0',
                'statement': [
                    {
                        'effect': 'allow',
                        'action': [
                            'cos:PutObject',
                            'cos:PostObject',
                            'cos:GetObject',
                            'cos:DeleteObject'
                        ],
                        'resource': [resource]
                    }
                ]
            })
        )
        
        credentials = response['Credentials']
        
        return Response({
            'tmpSecretId': credentials['AccessKeyId'],
            'tmpSecretKey': credentials['SecretAccessKey'],
            'sessionToken': credentials['SessionToken'],
            'expiredTime': int(credentials['Expiration'].timestamp()),
            'startTime': int(timezone.now().timestamp()),
            'requestId': response['RequestId']
        })
        
    except ClientError as e:
        logger.error(f'获取STS token失败: {str(e)}')
        return Response(
            {'error': f'获取临时凭证失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f'获取STS token失败: {str(e)}')
        return Response(
            {'error': f'获取临时凭证失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_to_cos(request):
    """
    通过后端上传文件到COS（适用于大文件或需要后端处理的场景）
    """
    try:
        # 检查COS服务是否启用
        if not cos_service.is_enabled():
            return Response(
                {'error': 'COS服务未启用'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 验证请求数据
        if 'file' not in request.FILES:
            return Response(
                {'error': '没有找到文件'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        user = request.user
        
        # 验证文件
        validation = cos_service.validate_file(file.read(), file.content_type)
        if not validation['valid']:
            return Response(
                {'error': validation['error']}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 重置文件指针
        file.seek(0)
        
        # 获取上传参数
        upload_request = CosUploadRequestSerializer(data=request.data)
        if not upload_request.is_valid():
            return Response(
                {'error': upload_request.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        folder = upload_request.validated_data.get('folder', 'images')
        upload_type = upload_request.validated_data.get('upload_type', 'dish_image')
        
        # 生成文件Key
        cos_key = cos_service.generate_file_key(file.name, folder, user.id)
        
        # 上传文件到COS
        upload_result = cos_service.upload_file(
            file.read(), 
            cos_key, 
            file.content_type
        )
        
        if not upload_result['success']:
            return Response(
                {'error': '文件上传失败'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 创建文件记录
        cos_file = CosFile.objects.create(
            user=user,
            file_key=cos_key,
            original_name=file.name,
            file_size=file.size,
            content_type=file.content_type,
            upload_type=upload_type,
            bucket=cos_service.config['bucket'],
            region=cos_service.config['region']
        )
        
        # 构建响应数据
        response_data = {
            'success': True,
            'url': upload_result['url'],
            'key': cos_key,
            'filename': file.name,
            'size': file.size,
            'etag': upload_result['etag'],
            'uploaded_at': timezone.now().isoformat(),
            'file_id': cos_file.id
        }
        
        serializer = CosUploadResponseSerializer(response_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f'上传文件到COS失败: {str(e)}')
        return Response(
            {'error': f'文件上传失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_from_cos(request, file_key):
    """
    删除COS中的文件
    """
    try:
        # 检查COS服务是否启用
        if not cos_service.is_enabled():
            return Response(
                {'error': 'COS服务未启用'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 检查用户是否有权限删除该文件
        try:
            cos_file = CosFile.objects.get(file_key=file_key, user=request.user)
        except CosFile.DoesNotExist:
            return Response(
                {'error': '文件不存在或没有权限删除'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 删除COS中的文件
        delete_result = cos_service.delete_file(file_key)
        
        if not delete_result['success']:
            return Response(
                {'error': '文件删除失败'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 删除数据库记录
        cos_file.delete()
        
        response_data = {
            'success': True,
            'message': '文件删除成功',
            'key': file_key
        }
        
        serializer = CosDeleteResponseSerializer(response_data)
        return Response(serializer.data)
        
    except CosClientError as e:
        logger.error(f'删除COS文件失败（客户端错误）: {str(e)}')
        return Response(
            {'error': f'删除文件失败: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except CosServiceError as e:
        logger.error(f'删除COS文件失败（服务错误）: {str(e)}')
        return Response(
            {'error': f'删除文件失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f'删除COS文件失败: {str(e)}')
        return Response(
            {'error': f'删除文件失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_user_files(request):
    """
    获取用户上传的文件列表
    """
    try:
        # 检查COS服务是否启用
        if not cos_service.is_enabled():
            return Response(
                {'error': 'COS服务未启用'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        user = request.user
        prefix = f"{cos_service.config.get('prefix', 'memoryday')}/images/user_{user.id}/"
        
        # 获取文件列表
        files = cos_service.list_files(prefix=prefix, max_keys=100)
        
        response_data = {
            'files': files,
            'total': len(files)
        }
        
        serializer = CosListResponseSerializer(response_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f'获取文件列表失败: {str(e)}')
        return Response(
            {'error': f'获取文件列表失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_file_info(request, file_key):
    """
    获取文件详细信息
    """
    try:
        # 检查COS服务是否启用
        if not cos_service.is_enabled():
            return Response(
                {'error': 'COS服务未启用'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 检查用户权限
        try:
            cos_file = CosFile.objects.get(file_key=file_key, user=request.user)
        except CosFile.DoesNotExist:
            return Response(
                {'error': '文件不存在或没有权限访问'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 获取文件信息
        file_info = cos_service.get_file_info(file_key)
        
        if not file_info:
            return Response(
                {'error': '获取文件信息失败'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 合并数据库信息和COS信息
        response_data = {
            **file_info,
            'id': cos_file.id,
            'original_name': cos_file.original_name,
            'upload_type': cos_file.upload_type,
            'upload_type_display': cos_file.get_upload_type_display(),
            'created_at': cos_file.created_at.isoformat(),
            'thumbnail_url': cos_file.thumbnail_url,
            'preview_url': cos_file.preview_url
        }
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f'获取文件信息失败: {str(e)}')
        return Response(
            {'error': f'获取文件信息失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_signed_url(request):
    """
    获取签名URL（用于私有读写存储桶）
    """
    try:
        # 检查COS服务是否启用
        if not cos_service.is_enabled():
            return Response(
                {'error': 'COS服务未启用'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 获取请求参数
        file_key = request.data.get('file_key')
        expires = request.data.get('expires', 3600)  # 默认1小时
        style = request.data.get('style', 'original')  # 图片处理样式
        
        if not file_key:
            return Response(
                {'error': '文件key不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 生成签名URL
        if style == 'original':
            signed_url = cos_service.get_file_url(file_key, expires)
        else:
            signed_url = cos_service.get_optimized_url(file_key, style)
        
        return Response({
            'success': True,
            'url': signed_url,
            'key': file_key,
            'expires': expires,
            'style': style
        })
        
    except Exception as e:
        logger.error(f'生成签名URL失败: {str(e)}')
        return Response(
            {'error': f'生成签名URL失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_batch_signed_urls(request):
    """
    批量获取签名URL
    """
    try:
        # 检查COS服务是否启用
        if not cos_service.is_enabled():
            return Response(
                {'error': 'COS服务未启用'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 获取请求参数
        file_keys = request.data.get('file_keys', [])
        expires = request.data.get('expires', 3600)  # 默认1小时
        style = request.data.get('style', 'original')  # 图片处理样式
        
        if not file_keys or not isinstance(file_keys, list):
            return Response(
                {'error': '文件key列表不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 批量生成签名URL
        urls = []
        for file_key in file_keys:
            if style == 'original':
                signed_url = cos_service.get_file_url(file_key, expires)
            else:
                signed_url = cos_service.get_optimized_url(file_key, style)
            
            urls.append({
                'key': file_key,
                'url': signed_url
            })
        
        return Response({
            'success': True,
            'urls': urls,
            'total': len(urls),
            'expires': expires,
            'style': style
        })
        
    except Exception as e:
        logger.error(f'批量生成签名URL失败: {str(e)}')
        return Response(
            {'error': f'批量生成签名URL失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_cos_status(request):
    """
    检查COS服务状态
    """
    try:
        status_info = {
            'enabled': cos_service.is_enabled(),
            'config_available': bool(cos_service.config),
            'client_available': cos_service.client is not None,
            'config_keys': list(cos_service.config.keys()) if cos_service.config else [],
            'timestamp': timezone.now().isoformat()
        }
        
        return Response(status_info)
        
    except Exception as e:
        logger.error(f'检查COS状态失败: {str(e)}')
        return Response(
            {'error': f'检查COS状态失败: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_cos_client():
    """
    获取COS客户端实例（兼容旧代码）
    """
    return cos_service.client


class CosFileListView(generics.ListAPIView):
    """COS文件记录列表视图"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CosFileSerializer
    
    def get_queryset(self):
        """获取当前用户的文件记录"""
        user = self.request.user
        queryset = CosFile.objects.filter(user=user)
        
        # 支持按上传类型过滤
        upload_type = self.request.query_params.get('upload_type')
        if upload_type:
            queryset = queryset.filter(upload_type=upload_type)
        
        # 支持按时间范围过滤
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')


class CosFileViewSet(generics.ListCreateAPIView):
    """COS文件记录视图集"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CosFileSerializer
    
    def get_queryset(self):
        """获取当前用户的文件记录"""
        user = self.request.user
        queryset = CosFile.objects.filter(user=user)
        
        # 支持按上传类型过滤
        upload_type = self.request.query_params.get('upload_type')
        if upload_type:
            queryset = queryset.filter(upload_type=upload_type)
        
        # 支持按时间范围过滤
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')


class CosFileDetailView(generics.RetrieveDestroyAPIView):
    """COS文件记录详情视图"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CosFileSerializer
    
    def get_queryset(self):
        """只允许用户访问自己的文件记录"""
        return CosFile.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """删除文件记录和COS中的文件"""
        instance = self.get_object()
        
        try:
            # 删除COS中的文件
            if cos_service.is_enabled():
                cos_service.delete_file(instance.file_key)
            
            # 删除数据库记录
            instance.delete()
            
            return Response({
                'success': True,
                'message': '文件删除成功',
                'key': instance.file_key
            })
            
        except Exception as e:
            logger.error(f'删除文件失败: {str(e)}')
            return Response(
                {'error': f'删除文件失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def get_cos_client():
    """
    获取COS客户端实例
    """
    config = getattr(settings, 'COS_CONFIG', {})
    
    cos_config = CosConfig(
        Region=config.get('region'),
        SecretId=config.get('secret_id'),
        SecretKey=config.get('secret_key')
    )
    
    return CosS3Client(cos_config)