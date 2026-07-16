from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta

from .models import UserStat
from apps.dishes.models import Dish
from apps.users.models import User


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_stats(request):
    """用户仪表盘统计"""
    user = request.user
    
    # 用户菜品统计
    total_dishes = Dish.objects.filter(author=user).count()
    public_dishes = Dish.objects.filter(author=user, is_public=True).count()
    
    # 最近7天活跃度
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_dishes = Dish.objects.filter(
        author=user, 
        created_at__gte=seven_days_ago
    ).count()
    
    # 分类统计
    category_stats = Dish.objects.filter(author=user, category__isnull=False).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 难度统计
    difficulty_stats = Dish.objects.filter(author=user).values('difficulty').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return Response({
        'total_dishes': total_dishes,
        'public_dishes': public_dishes,
        'recent_activity': recent_dishes,
        'category_stats': list(category_stats),
        'difficulty_stats': list(difficulty_stats),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def global_stats(request):
    """全局统计信息"""
    total_users = User.objects.count()
    total_dishes = Dish.objects.count()
    avg_dishes_per_user = Dish.objects.values('author').annotate(
        dish_count=Count('id')
    ).aggregate(avg=Avg('dish_count'))['avg'] or 0
    
    # 热门分类
    popular_categories = Dish.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # 最近活跃用户
    seven_days_ago = datetime.now() - timedelta(days=7)
    active_users = User.objects.filter(
        created_dishes__created_at__gte=seven_days_ago
    ).annotate(
        dish_count=Count('dish')
    ).order_by('-dish_count')[:10]
    
    return Response({
        'total_users': total_users,
        'total_dishes': total_dishes,
        'avg_dishes_per_user': round(avg_dishes_per_user, 1),
        'popular_categories': list(popular_categories),
        'active_users_count': active_users.count(),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_activity_timeline(request):
    """用户活动时间线"""
    user = request.user
    activities = []
    
    # 添加菜品创建活动
    dishes = Dish.objects.filter(author=user).order_by('-created_at')[:20]
    for dish in dishes:
        activities.append({
            'type': 'dish_created',
            'title': f'创建了菜品: {dish.name}',
            'description': dish.description[:100] + '...' if len(dish.description) > 100 else dish.description,
            'timestamp': dish.created_at,
            'data': {
                'dish_id': dish.id,
                'dish_name': dish.name,
                'category': dish.category,
            }
        })
    
    # 按时间排序
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response({'activities': activities[:10]})


class UserStatListView(generics.ListAPIView):
    """用户统计列表视图"""
    serializer_class = None  # 不需要序列化器，直接返回数据
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        stats = UserStat.objects.filter(user=user).order_by('-date')
        
        # 格式化统计数据
        formatted_stats = []
        for stat in stats:
            formatted_stats.append({
                'date': stat.date,
                'dishes_created': stat.dishes_created,
                'dishes_viewed': stat.dishes_viewed,
                'time_spent': stat.time_spent,
            })
        
        return Response({'stats': formatted_stats})