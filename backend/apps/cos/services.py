"""
腾讯云COS服务类
提供文件上传、下载、删除、列表等操作
"""
import uuid
import logging
from django.conf import settings
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class CosService:
    """腾讯云COS服务类"""
    
    def __init__(self):
        self.config = getattr(settings, 'COS_CONFIG', {})
        self.client = self._get_client()
    
    def _get_client(self) -> Optional[CosS3Client]:
        """获取COS客户端"""
        if not self.config.get('enabled'):
            return None
            
        try:
            cos_config = CosConfig(
                Region=self.config.get('region'),
                SecretId=self.config.get('secret_id'),
                SecretKey=self.config.get('secret_key')
            )
            return CosS3Client(cos_config)
        except Exception as e:
            logger.error(f'创建COS客户端失败: {str(e)}')
            return None
    
    def is_enabled(self) -> bool:
        """检查COS服务是否启用"""
        return self.config.get('enabled', False) and self.client is not None
    
    def generate_file_key(self, original_filename: str, folder: str = 'images', 
                         user_id: Optional[int] = None) -> str:
        """生成唯一的文件Key"""
        file_ext = original_filename.split('.')[-1] if '.' in original_filename else 'jpg'
        filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        prefix = self.config.get('prefix', 'memoryday')
        if user_id:
            return f"{prefix}/{folder}/user_{user_id}/{filename}"
        else:
            return f"{prefix}/{folder}/{filename}"
    
    def upload_file(self, file_content: bytes, file_key: str, 
                   content_type: str = 'image/jpeg') -> Dict[str, Any]:
        """上传文件到COS"""
        if not self.is_enabled():
            raise Exception('COS服务未启用')
        
        try:
            response = self.client.put_object(
                Bucket=self.config['bucket'],
                Key=file_key,
                Body=file_content,
                ContentType=content_type
            )
            
            return {
                'success': True,
                'key': file_key,
                'etag': response.get('ETag', ''),
                'url': self.get_file_url(file_key),
                'request_id': response.get('RequestId', '')
            }
            
        except CosClientError as e:
            logger.error(f'COS客户端错误: {str(e)}')
            raise Exception(f'上传文件失败: {str(e)}')
        except CosServiceError as e:
            logger.error(f'COS服务错误: {str(e)}')
            raise Exception(f'上传文件失败: {str(e)}')
        except Exception as e:
            logger.error(f'上传文件异常: {str(e)}')
            raise Exception(f'上传文件失败: {str(e)}')
    
    def delete_file(self, file_key: str) -> Dict[str, Any]:
        """删除COS中的文件"""
        if not self.is_enabled():
            raise Exception('COS服务未启用')
        
        try:
            response = self.client.delete_object(
                Bucket=self.config['bucket'],
                Key=file_key
            )
            
            return {
                'success': True,
                'key': file_key,
                'request_id': response.get('RequestId', '')
            }
            
        except CosClientError as e:
            logger.error(f'删除文件客户端错误: {str(e)}')
            raise Exception(f'删除文件失败: {str(e)}')
        except CosServiceError as e:
            logger.error(f'删除文件服务错误: {str(e)}')
            raise Exception(f'删除文件失败: {str(e)}')
        except Exception as e:
            logger.error(f'删除文件异常: {str(e)}')
            raise Exception(f'删除文件失败: {str(e)}')
    
    def get_file_info(self, file_key: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        if not self.is_enabled():
            return None
        
        try:
            response = self.client.head_object(
                Bucket=self.config['bucket'],
                Key=file_key
            )
            
            return {
                'key': file_key,
                'size': response.get('Content-Length', 0),
                'content_type': response.get('Content-Type', ''),
                'last_modified': response.get('Last-Modified', ''),
                'etag': response.get('ETag', ''),
                'url': self.get_file_url(file_key)
            }
            
        except Exception as e:
            logger.warning(f'获取文件信息失败: {str(e)}')
            return None
    
    def list_files(self, prefix: str = '', max_keys: int = 100) -> List[Dict[str, Any]]:
        """列出文件"""
        if not self.is_enabled():
            return []
        
        try:
            response = self.client.list_objects(
                Bucket=self.config['bucket'],
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            if 'Contents' in response:
                for item in response['Contents']:
                    files.append({
                        'key': item['Key'],
                        'size': item['Size'],
                        'last_modified': item['LastModified'],
                        'etag': item['ETag'],
                        'url': self.get_file_url(item['Key'])
                    })
            
            return files
            
        except Exception as e:
            logger.error(f'列出文件失败: {str(e)}')
            return []
    
    def get_file_url(self, file_key: str, expires: int = 3600) -> str:
        """获取文件URL"""
        if not self.is_enabled():
            return ''
        
        # 私有读写存储桶需要生成签名URL
        if self.config.get('use_signed_url', True):
            try:
                # 生成带签名的URL
                url = self.client.get_presigned_url(
                    Method='GET',
                    Bucket=self.config['bucket'],
                    Key=file_key,
                    Expired=expires
                )
                return url
            except Exception as e:
                logger.warning(f'生成签名URL失败，返回无签名URL: {str(e)}')
                # 降级方案：返回无签名URL
        
        # 如果有自定义域名，优先使用
        domain = self.config.get('domain')
        if domain:
            return f"https://{domain}/{file_key}"
        
        # 否则使用腾讯云默认域名
        return f"https://{self.config['bucket']}.cos.{self.config['region']}.myqcloud.com/{file_key}"
    
    def get_optimized_url(self, file_key: str, style: str = 'thumbnail') -> str:
        """获取优化后的图片URL"""
        base_url = self.get_file_url(file_key)
        
        # 图片处理样式
        styles = {
            'thumbnail': 'imageView2/1/w/200/h/200',  # 缩略图
            'preview': 'imageView2/0/q/80',           # 预览图
            'detail': 'imageView2/0/q/90',            # 详情图
            'original': ''                            # 原图
        }
        
        style_param = styles.get(style, styles['thumbnail'])
        if style_param:
            # 对于签名URL，需要将处理参数添加到签名中
            if self.config.get('use_signed_url', True) and '?' in base_url:
                # 签名URL已包含签名参数，直接添加处理参数
                return f"{base_url}&{style_param}"
            else:
                # 无签名URL，直接添加参数
                return f"{base_url}?{style_param}"
        else:
            return base_url
    
    def get_optimized_url(self, file_key: str, style: str = 'thumbnail') -> str:
        """获取优化后的图片URL"""
        base_url = self.get_file_url(file_key)
        
        # 图片处理样式
        styles = {
            'thumbnail': 'imageView2/1/w/200/h/200',  # 缩略图
            'preview': 'imageView2/0/q/80',           # 预览图
            'detail': 'imageView2/0/q/90',            # 详情图
            'original': ''                            # 原图
        }
        
        style_param = styles.get(style, styles['thumbnail'])
        if style_param:
            return f"{base_url}?{style_param}"
        else:
            return base_url
    
    def validate_file(self, file_content: bytes, content_type: str) -> Dict[str, Any]:
        """验证文件"""
        max_size = self.config.get('max_file_size', 5 * 1024 * 1024)
        allowed_types = self.config.get('allowed_types', [])
        
        # 检查文件大小
        if len(file_content) > max_size:
            return {
                'valid': False,
                'error': f'文件大小不能超过{max_size // 1024 // 1024}MB'
            }
        
        # 检查文件类型
        if allowed_types and content_type not in allowed_types:
            return {
                'valid': False,
                'error': f'不支持的文件类型: {content_type}'
            }
        
        return {'valid': True, 'error': ''}


# 全局COS服务实例
cos_service = CosService()