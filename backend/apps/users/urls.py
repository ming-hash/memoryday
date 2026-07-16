from django.urls import path
from . import views

urlpatterns = [
    # 用户认证
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('wechat-login/', views.wechat_login, name='wechat-login'),
    path('send-sms-code/', views.send_sms_code, name='send-sms-code'),
    
    # 用户管理
    path('', views.UserListView.as_view(), name='user-list'),
    path('me/', views.UserDetailView.as_view(), name='user-detail'),
]