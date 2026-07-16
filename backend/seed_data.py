"""
Seed data script - creates test user and sample dishes
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memoryday_backend.settings.development')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from apps.users.models import User
from apps.dishes.models import Dish, DishCategory


def seed():
    # 1. Create test user (force reset password every time)
    user, created = User.objects.get_or_create(
        phone='13800138000',
        defaults={
            'nickname': 'Admin',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
        }
    )
    # Always reset password to ensure it's correct
    user.set_password('admin123')
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save()
    if created:
        print('[OK] Created super admin: 13800138000')
    else:
        print('[OK] Reset password for existing admin: 13800138000')

    # 2. Create categories
    categories = {
        'chinese': 'Chinese Food',
        'western': 'Western Food',
        'japanese': 'Japanese Food',
        'korean': 'Korean Food',
        'dessert': 'Desserts & Drinks',
    }

    cat_objs = {}
    for code, name in categories.items():
        cat, _ = DishCategory.objects.get_or_create(name=name, defaults={'is_active': True})
        cat_objs[code] = cat
    print('[OK] Created %d categories' % len(cat_objs))

    # 3. Create sample dishes
    sample_dishes = [
        {
            'name': 'Tomato Scrambled Eggs',
            'description': 'Classic Chinese home-style dish, simple and delicious',
            'story': 'The first dish my mom taught me',
            'cooking_time': 15,
            'difficulty': 'easy',
            'cooking_method': 'stir_fry',
            'cuisine_type': 'chinese',
            'category': 'chinese',
            'ingredients': [
                {'name': 'Eggs', 'amount': '3 pcs'},
                {'name': 'Tomatoes', 'amount': '2 pcs'},
                {'name': 'Green Onion', 'amount': 'some'},
                {'name': 'Salt', 'amount': 'to taste'},
            ],
            'steps': [
                {'step': 1, 'content': 'Beat eggs with a pinch of salt', 'image': ''},
                {'step': 2, 'content': 'Cut tomatoes into chunks', 'image': ''},
                {'step': 3, 'content': 'Fry eggs until set, remove from pan', 'image': ''},
                {'step': 4, 'content': 'Cook tomatoes until soft', 'image': ''},
                {'step': 5, 'content': 'Add eggs back and stir-fry together', 'image': ''},
            ],
            'tips': 'Let tomatoes release their juice for better flavor',
            'rating': 4.8,
            'cooked_count': 42,
            'view_count': 230,
            'favorite_count': 18,
        },
        {
            'name': 'Braised Pork Ribs',
            'description': 'Rich red color, tender meat that melts in your mouth',
            'story': 'A must-have dish for every family gathering',
            'cooking_time': 60,
            'difficulty': 'medium',
            'cooking_method': 'stew',
            'cuisine_type': 'chinese',
            'category': 'chinese',
            'ingredients': [
                {'name': 'Pork Ribs', 'amount': '500g'},
                {'name': 'Light Soy Sauce', 'amount': '2 tbsp'},
                {'name': 'Dark Soy Sauce', 'amount': '1 tbsp'},
                {'name': 'Rock Sugar', 'amount': '30g'},
                {'name': 'Star Anise', 'amount': '2 pcs'},
            ],
            'steps': [
                {'step': 1, 'content': 'Blanch ribs to remove blood', 'image': ''},
                {'step': 2, 'content': 'Caramelize sugar until golden', 'image': ''},
                {'step': 3, 'content': 'Add ribs and coat with caramel', 'image': ''},
                {'step': 4, 'content': 'Add seasonings and water, simmer 40 min', 'image': ''},
                {'step': 5, 'content': 'Reduce sauce on high heat', 'image': ''},
            ],
            'tips': 'Rinse with warm water after blanching to keep meat tender',
            'rating': 4.9,
            'cooked_count': 35,
            'view_count': 189,
            'favorite_count': 25,
        },
        {
            'name': 'Teriyaki Chicken',
            'description': 'Rich sauce, tender and juicy chicken thighs',
            'cooking_time': 30,
            'difficulty': 'medium',
            'cooking_method': 'fry',
            'cuisine_type': 'japanese',
            'category': 'japanese',
            'ingredients': [
                {'name': 'Chicken Thigh', 'amount': '2 pcs'},
                {'name': 'Soy Sauce', 'amount': '3 tbsp'},
                {'name': 'Mirin', 'amount': '2 tbsp'},
                {'name': 'Honey', 'amount': '1 tbsp'},
                {'name': 'Ginger Slices', 'amount': '3 pcs'},
            ],
            'steps': [
                {'step': 1, 'content': 'Debone chicken, poke holes with fork', 'image': ''},
                {'step': 2, 'content': 'Mix teriyaki sauce', 'image': ''},
                {'step': 3, 'content': 'Fry skin-side down until golden', 'image': ''},
                {'step': 4, 'content': 'Flip and pour in sauce', 'image': ''},
                {'step': 5, 'content': 'Simmer until sauce thickens', 'image': ''},
            ],
            'tips': 'Frying skin-side first renders excess fat',
            'rating': 4.7,
            'cooked_count': 28,
            'view_count': 156,
            'favorite_count': 15,
        },
        {
            'name': 'Kimchi Fried Rice',
            'description': 'Spicy and tangy, quick and delicious Korean fried rice',
            'cooking_time': 20,
            'difficulty': 'easy',
            'cooking_method': 'stir_fry',
            'cuisine_type': 'korean',
            'category': 'korean',
            'ingredients': [
                {'name': 'Rice', 'amount': '2 bowls'},
                {'name': 'Kimchi', 'amount': '150g'},
                {'name': 'Pork Belly', 'amount': '100g'},
                {'name': 'Egg', 'amount': '1 pc'},
                {'name': 'Gochujang', 'amount': '1 tbsp'},
            ],
            'steps': [
                {'step': 1, 'content': 'Slice pork belly thin', 'image': ''},
                {'step': 2, 'content': 'Fry pork belly until crispy', 'image': ''},
                {'step': 3, 'content': 'Add kimchi and stir-fry', 'image': ''},
                {'step': 4, 'content': 'Add rice and mix well', 'image': ''},
                {'step': 5, 'content': 'Top with a fried egg', 'image': ''},
            ],
            'tips': 'Use day-old rice for best texture',
            'rating': 4.5,
            'cooked_count': 20,
            'view_count': 98,
            'favorite_count': 12,
        },
        {
            'name': 'Tiramisu',
            'description': 'Classic Italian dessert, perfect blend of coffee and cream',
            'cooking_time': 40,
            'difficulty': 'hard',
            'cooking_method': 'other',
            'cuisine_type': 'western',
            'category': 'dessert',
            'ingredients': [
                {'name': 'Mascarpone', 'amount': '250g'},
                {'name': 'Ladyfingers', 'amount': '200g'},
                {'name': 'Espresso', 'amount': '200ml'},
                {'name': 'Eggs', 'amount': '3 pcs'},
                {'name': 'Cocoa Powder', 'amount': 'to taste'},
            ],
            'steps': [
                {'step': 1, 'content': 'Beat egg yolks with sugar', 'image': ''},
                {'step': 2, 'content': 'Fold in mascarpone cheese', 'image': ''},
                {'step': 3, 'content': 'Whip egg whites to stiff peaks', 'image': ''},
                {'step': 4, 'content': 'Dip ladyfingers in espresso', 'image': ''},
                {'step': 5, 'content': 'Layer cheese mixture and ladyfingers', 'image': ''},
                {'step': 6, 'content': 'Refrigerate 4+ hours, dust with cocoa', 'image': ''},
            ],
            'tips': 'Do not soak ladyfingers too long, keep the texture',
            'rating': 4.6,
            'cooked_count': 15,
            'view_count': 120,
            'favorite_count': 22,
        },
    ]

    created_count = 0
    for dish_data in sample_dishes:
        category_code = dish_data.pop('category')
        category = cat_objs.get(category_code)
        dish, created = Dish.objects.get_or_create(
            name=dish_data['name'],
            author=user,
            defaults={
                **dish_data,
                'category': category,
                'is_public': True,
                'is_active': True,
            }
        )
        if created:
            created_count += 1

    print('[OK] Created %d sample dishes (total: %d)' % (created_count, Dish.objects.count()))
    print('')
    print('=== Seed data complete! ===')
    print('Admin account: 13800138000')
    print('Admin password: admin123')
    print('')
    print('IMPORTANT: Use these exact credentials to login at http://127.0.0.1:8000/admin/')


if __name__ == '__main__':
    seed()
