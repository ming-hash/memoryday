# -*- coding: utf-8 -*-
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memoryday_backend.settings.development')
django.setup()

from apps.dishes.models import Dish, DishCategory, DishTag
from apps.users.models import User

def add_test_data():
    user = User.objects.first()
    if not user:
        print("No user found. Creating test user...")
        user = User.objects.create_user(phone='13800138000', password='test123')
    
    # 创建分类
    cat_chinese, _ = DishCategory.objects.get_or_create(
        name='家常菜', 
        defaults={'description': '普通家庭料理'}
    )
    cat_sichuan, _ = DishCategory.objects.get_or_create(
        name='川菜', 
        defaults={'description': '四川特色美食'}
    )
    cat_cantonese, _ = DishCategory.objects.get_or_create(
        name='粤菜', 
        defaults={'description': '广东特色美食'}
    )
    
    # 创建标签
    tag_spicy, _ = DishTag.objects.get_or_create(
        name='辣', 
        defaults={'description': '辣味'}
    )
    tag_healthy, _ = DishTag.objects.get_or_create(
        name='健康', 
        defaults={'description': '健康饮食'}
    )
    tag_quick, _ = DishTag.objects.get_or_create(
        name='快手', 
        defaults={'description': '简单快捷'}
    )
    
    # 菜品数据
    dishes_data = [
        {
            'name': '宫保鸡丁',
            'description': '经典川菜，鸡肉嫩滑，花生香脆',
            'cooking_time': 20,
            'difficulty': 'medium',
            'cooking_method': 'stir_fry',
            'cuisine_type': 'chinese',
            'category': cat_sichuan,
            'ingredients': ['鸡胸肉', '花生', '干辣椒', '花椒', '葱', '姜', '蒜', '酱油', '醋', '糖'],
            'steps': ['鸡胸肉切丁，用料酒和盐腌制10分钟', '调制酱汁：酱油、醋、糖、淀粉、水', '热油爆香花椒和干辣椒', '加入鸡丁快炒至变色', '倒入酱汁翻炒均匀', '撒入花生和葱花即可']
        },
        {
            'name': '红烧肉',
            'description': '软糯入味，肥而不腻',
            'cooking_time': 60,
            'difficulty': 'medium',
            'cooking_method': 'braise',
            'cuisine_type': 'chinese',
            'category': cat_chinese,
            'ingredients': ['五花肉', '冰糖', '生抽', '老抽', '料酒', '八角', '桂皮', '葱', '姜'],
            'steps': ['五花肉切块，冷水下锅焯水', '热油炒糖色', '加入肉块翻炒上色', '加入调料和适量水', '小火炖煮1小时', '大火收汁即可']
        },
        {
            'name': '清蒸鲈鱼',
            'description': '鱼肉鲜嫩，清淡可口',
            'cooking_time': 25,
            'difficulty': 'hard',
            'cooking_method': 'steam',
            'cuisine_type': 'cantonese',
            'category': cat_cantonese,
            'ingredients': ['鲈鱼', '葱', '姜', '蒸鱼豉油', '料酒', '盐'],
            'steps': ['鲈鱼处理干净，两面划刀', '鱼身抹盐和料酒腌制10分钟', '铺上葱姜', '水开后放入蒸10分钟', '倒掉蒸出的水', '淋上蒸鱼豉油，泼热油即可']
        },
        {
            'name': '麻婆豆腐',
            'description': '麻辣鲜香，下饭神器',
            'cooking_time': 15,
            'difficulty': 'easy',
            'cooking_method': 'stir_fry',
            'cuisine_type': 'chinese',
            'category': cat_sichuan,
            'ingredients': ['嫩豆腐', '肉末', '豆瓣酱', '花椒', '蒜末', '葱花', '酱油', '淀粉'],
            'steps': ['豆腐切小块焯水', '热油爆香蒜末和花椒', '加入肉末炒散', '加入豆瓣酱炒出红油', '加入豆腐和适量水', '勾芡收汁，撒葱花即可']
        },
        {
            'name': '蛋炒饭',
            'description': '简单美味，剩饭的最佳归宿',
            'cooking_time': 10,
            'difficulty': 'easy',
            'cooking_method': 'stir_fry',
            'cuisine_type': 'chinese',
            'category': cat_chinese,
            'ingredients': ['隔夜米饭', '鸡蛋', '葱花', '盐', '酱油'],
            'steps': ['鸡蛋打散', '热油炒蛋液', '加入米饭翻炒', '加入盐和少许酱油', '撒葱花翻炒均匀即可']
        },
        {
            'name': '可乐鸡翅',
            'description': '甜香可口，色泽红亮',
            'cooking_time': 30,
            'difficulty': 'easy',
            'cooking_method': 'braise',
            'cuisine_type': 'chinese',
            'category': cat_chinese,
            'ingredients': ['鸡翅中', '可乐', '生抽', '姜', '料酒'],
            'steps': ['鸡翅焯水去腥', '热油煎至两面金黄', '加入姜片和料酒', '倒入可乐和生抽', '中火煮20分钟', '大火收汁即可']
        },
        {
            'name': '酸辣土豆丝',
            'description': '爽脆开胃，经典下饭菜',
            'cooking_time': 15,
            'difficulty': 'easy',
            'cooking_method': 'stir_fry',
            'cuisine_type': 'chinese',
            'category': cat_sichuan,
            'ingredients': ['土豆', '干辣椒', '花椒', '醋', '盐', '蒜'],
            'steps': ['土豆切丝泡水去淀粉', '热油爆香花椒和干辣椒', '加入土豆丝大火快炒', '加入醋和盐调味', '翻炒均匀即可']
        }
    ]
    
    created = 0
    for data in dishes_data:
        dish, is_new = Dish.objects.get_or_create(
            name=data['name'],
            author=user,
            defaults={
                'description': data['description'],
                'cooking_time': data['cooking_time'],
                'difficulty': data['difficulty'],
                'cooking_method': data['cooking_method'],
                'cuisine_type': data['cuisine_type'],
                'category': data['category'],
                'ingredients': data['ingredients'],
                'steps': data['steps'],
            }
        )
        if is_new:
            dish.tags.add(tag_spicy, tag_quick)
            created += 1
            print(f'Created: {dish.name}')
        else:
            print(f'Already exists: {dish.name}')
    
    print(f'\nTotal dishes: {Dish.objects.count()}')
    print(f'Created new dishes: {created}')

if __name__ == '__main__':
    add_test_data()
