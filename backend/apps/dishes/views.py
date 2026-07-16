from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Dish, DishFavorite
from .serializers import DishSerializer, DishCreateSerializer


class DishListView(generics.ListCreateAPIView):
    """菜品列表视图"""
    queryset = Dish.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty', 'is_public', 'is_active']
    search_fields = ['name', 'description', 'ingredients']
    ordering_fields = ['created_at', 'updated_at', 'cooking_time', 'difficulty', 'rating']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DishCreateSerializer
        return DishSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class DishDetailView(generics.RetrieveUpdateDestroyAPIView):
    """菜品详情视图"""
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UserDishListView(generics.ListAPIView):
    """用户菜品列表视图"""
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Dish.objects.filter(author=self.request.user)


class UserFavoriteListView(generics.ListAPIView):
    """用户收藏列表视图"""
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Dish.objects.filter(favorites__user=self.request.user)


class RecommendedDishListView(generics.ListAPIView):
    """推荐菜品列表视图"""
    serializer_class = DishSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Dish.objects.filter(is_public=True).order_by('-rating', '-cooked_count')[:10]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def random_dish(request):
    """随机获取一个菜品"""
    dish = Dish.objects.filter(is_public=True).order_by('?').first()
    if dish:
        serializer = DishSerializer(dish)
        return Response(serializer.data)
    return Response({'message': '暂无菜品'}, status=404)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_dishes(request):
    """搜索菜品"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    difficulty = request.GET.get('difficulty', '')
    
    queryset = Dish.objects.filter(is_public=True)
    
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query)
        )
    
    if category:
        queryset = queryset.filter(category=category)
    
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)
    
    serializer = DishSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite(request, dish_id):
    """切换收藏状态"""
    try:
        dish = Dish.objects.get(id=dish_id)
    except Dish.DoesNotExist:
        return Response({'error': '菜品不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    favorite, created = DishFavorite.objects.get_or_create(
        user=request.user,
        dish=dish
    )
    
    if request.method == 'DELETE':
        favorite.delete()
        dish.favorite_count = max(0, dish.favorite_count - 1)
        dish.save(update_fields=['favorite_count'])
        return Response({'message': '取消收藏成功', 'is_favorited': False})
    
    return Response({
        'message': '收藏成功',
        'is_favorited': True,
        'favorite_id': str(favorite.id)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_favorite(request, dish_id):
    """检查是否已收藏"""
    try:
        dish = Dish.objects.get(id=dish_id)
    except Dish.DoesNotExist:
        return Response({'error': '菜品不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    is_favorited = DishFavorite.objects.filter(
        user=request.user,
        dish=dish
    ).exists()
    
    return Response({
        'is_favorited': is_favorited,
        'favorite_count': dish.favorite_count
    })