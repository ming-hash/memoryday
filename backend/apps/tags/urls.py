from django.urls import path
from . import views

urlpatterns = [
    # 标签管理
    path('', views.TagListView.as_view(), name='tag-list'),
    path('<int:pk>/', views.TagDetailView.as_view(), name='tag-detail'),
    
    # 标签功能
    path('popular/', views.popular_tags, name='popular-tags'),
    path('search/', views.search_tags, name='search-tags'),
]