from django.urls import path
from . import views

urlpatterns = [
    # 统计功能
    path('dashboard/', views.user_dashboard_stats, name='user-dashboard'),
    path('global/', views.global_stats, name='global-stats'),
    path('activity/', views.user_activity_timeline, name='user-activity'),
    path('user-stats/', views.UserStatListView.as_view(), name='user-stats-list'),
]