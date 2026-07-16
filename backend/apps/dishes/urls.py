from django.urls import path
from . import views

urlpatterns = [
    # 菜品管理
    path('', views.DishListView.as_view(), name='dish-list'),
    path('<uuid:pk>/', views.DishDetailView.as_view(), name='dish-detail'),
    
    # 用户菜品
    path('my-dishes/', views.UserDishListView.as_view(), name='user-dish-list'),
    
    # 收藏功能
    path('favorites/', views.UserFavoriteListView.as_view(), name='user-favorites'),
    path('<uuid:dish_id>/favorite/', views.toggle_favorite, name='toggle-favorite'),
    path('<uuid:dish_id>/check-favorite/', views.check_favorite, name='check-favorite'),
    
    # 推荐菜品
    path('recommended/', views.RecommendedDishListView.as_view(), name='recommended-dishes'),
    path('random/', views.random_dish, name='random-dish'),
    
    # 搜索功能
    path('search/', views.search_dishes, name='search-dishes'),
]