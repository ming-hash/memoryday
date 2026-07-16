from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count

from .models import Tag
from .serializers import TagSerializer


class TagListView(generics.ListCreateAPIView):
    """标签列表视图"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    """标签详情视图"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_tags(request):
    """获取热门标签"""
    tags = Tag.objects.annotate(dish_count=Count('dishes')).order_by('-dish_count')[:10]
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_tags(request):
    """搜索标签"""
    query = request.GET.get('q', '')
    if query:
        tags = Tag.objects.filter(name__icontains=query)
    else:
        tags = Tag.objects.all()
    
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)