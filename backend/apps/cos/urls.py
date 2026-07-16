from django.urls import path
from . import views

urlpatterns = [
    # 文件记录管理接口
    path('files/', views.CosFileListView.as_view(), name='cosfile-list'),
    
    # STS临时凭证接口
    path('sts-token/', views.get_sts_token, name='cos-sts-token'),
    
    # 文件上传接口
    path('upload/', views.upload_to_cos, name='cos-upload'),
    
    # 文件管理接口
    path('delete/<str:file_key>/', views.delete_from_cos, name='cos-delete'),
    path('list/', views.list_user_files, name='cos-list'),
    path('info/<str:file_key>/', views.get_file_info, name='cos-info'),
    
    # 签名URL接口（私有读写存储桶）
    path('signed-url/', views.get_signed_url, name='cos-signed-url'),
    path('batch-signed-urls/', views.get_batch_signed_urls, name='cos-batch-signed-urls'),
    
    # 服务状态检查
    path('status/', views.check_cos_status, name='cos-status'),
]