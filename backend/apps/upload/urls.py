from django.urls import path
from . import views

urlpatterns = [
    # 文件上传
    path('upload/', views.upload_file, name='upload-file'),
    path('my-uploads/', views.user_uploads, name='user-uploads'),
    path('delete/<int:file_id>/', views.delete_upload, name='delete-upload'),
    
    # 健康检查
    path('health/', views.health_check, name='health-check'),
]