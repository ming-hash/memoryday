"""
COS应用测试用例
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from .models import CosFile
from .services import cos_service


class CosServiceTestCase(TestCase):
    """COS服务测试用例"""
    
    def setUp(self):
        """测试设置"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_cos_service_initialization(self):
        """测试COS服务初始化"""
        # 检查服务是否可用
        self.assertIsNotNone(cos_service)
        
        # 检查配置
        config = getattr(settings, 'COS_CONFIG', {})
        self.assertIsInstance(config, dict)
    
    def test_generate_file_key(self):
        """测试生成文件Key"""
        filename = "test.jpg"
        folder = "images"
        user_id = self.user.id
        
        # 生成带用户ID的文件Key
        key1 = cos_service.generate_file_key(filename, folder, user_id)
        self.assertIn(f"user_{user_id}", key1)
        self.assertIn("images", key1)
        self.assertIn(".jpg", key1)
        
        # 生成不带用户ID的文件Key
        key2 = cos_service.generate_file_key(filename, folder)
        self.assertIn("images", key2)
        self.assertNotIn(f"user_{user_id}", key2)
    
    def test_url_generation(self):
        """测试URL生成"""
        file_key = "test/file.jpg"
        
        # 测试基础URL生成
        base_url = cos_service.get_file_url(file_key)
        self.assertIsInstance(base_url, str)
        
        # 测试优化URL生成
        thumbnail_url = cos_service.get_optimized_url(file_key, 'thumbnail')
        self.assertIn('?imageView2', thumbnail_url)
        
        preview_url = cos_service.get_optimized_url(file_key, 'preview')
        self.assertIn('?imageView2', preview_url)
        
        detail_url = cos_service.get_optimized_url(file_key, 'detail')
        self.assertIn('?imageView2', detail_url)
        
        original_url = cos_service.get_optimized_url(file_key, 'original')
        self.assertEqual(original_url, base_url)


class CosFileModelTestCase(TestCase):
    """COS文件模型测试用例"""
    
    def setUp(self):
        """测试设置"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_cos_file(self):
        """测试创建COS文件记录"""
        cos_file = CosFile.objects.create(
            user=self.user,
            file_key="test/image.jpg",
            original_name="image.jpg",
            file_size=1024,
            content_type="image/jpeg",
            upload_type="dish_image",
            bucket="test-bucket",
            region="ap-beijing"
        )
        
        self.assertEqual(cos_file.user, self.user)
        self.assertEqual(cos_file.file_key, "test/image.jpg")
        self.assertEqual(cos_file.original_name, "image.jpg")
        self.assertEqual(cos_file.file_size, 1024)
        self.assertEqual(cos_file.content_type, "image/jpeg")
        self.assertEqual(cos_file.upload_type, "dish_image")
        self.assertEqual(cos_file.bucket, "test-bucket")
        self.assertEqual(cos_file.region, "ap-beijing")
    
    def test_file_url_property(self):
        """测试文件URL属性"""
        cos_file = CosFile.objects.create(
            user=self.user,
            file_key="test/image.jpg",
            original_name="image.jpg",
            file_size=1024,
            content_type="image/jpeg",
            upload_type="dish_image",
            bucket="test-bucket",
            region="ap-beijing"
        )
        
        expected_url = "https://test-bucket.cos.ap-beijing.myqcloud.com/test/image.jpg"
        self.assertEqual(cos_file.file_url, expected_url)
    
    def test_thumbnail_url_property(self):
        """测试缩略图URL属性"""
        cos_file = CosFile.objects.create(
            user=self.user,
            file_key="test/image.jpg",
            original_name="image.jpg",
            file_size=1024,
            content_type="image/jpeg",
            upload_type="dish_image",
            bucket="test-bucket",
            region="ap-beijing"
        )
        
        expected_url = "https://test-bucket.cos.ap-beijing.myqcloud.com/test/image.jpg?imageView2/1/w/200/h/200"
        self.assertEqual(cos_file.thumbnail_url, expected_url)
    
    def test_preview_url_property(self):
        """测试预览图URL属性"""
        cos_file = CosFile.objects.create(
            user=self.user,
            file_key="test/image.jpg",
            original_name="image.jpg",
            file_size=1024,
            content_type="image/jpeg",
            upload_type="dish_image",
            bucket="test-bucket",
            region="ap-beijing"
        )
        
        expected_url = "https://test-bucket.cos.ap-beijing.myqcloud.com/test/image.jpg?imageView2/0/q/80"
        self.assertEqual(cos_file.preview_url, expected_url)
    
    def test_get_file_info_method(self):
        """测试获取文件信息方法"""
        cos_file = CosFile.objects.create(
            user=self.user,
            file_key="test/image.jpg",
            original_name="image.jpg",
            file_size=1024,
            content_type="image/jpeg",
            upload_type="dish_image",
            bucket="test-bucket",
            region="ap-beijing"
        )
        
        file_info = cos_file.get_file_info()
        
        self.assertEqual(file_info['id'], cos_file.id)
        self.assertEqual(file_info['key'], cos_file.file_key)
        self.assertEqual(file_info['original_name'], cos_file.original_name)
        self.assertEqual(file_info['url'], cos_file.file_url)
        self.assertEqual(file_info['thumbnail_url'], cos_file.thumbnail_url)
        self.assertEqual(file_info['preview_url'], cos_file.preview_url)
        self.assertEqual(file_info['size'], cos_file.file_size)
        self.assertEqual(file_info['content_type'], cos_file.content_type)
        self.assertEqual(file_info['upload_type'], cos_file.upload_type)
        self.assertEqual(file_info['user_id'], cos_file.user_id)


class CosServiceValidationTestCase(TestCase):
    """COS服务验证测试用例"""
    
    def test_file_validation(self):
        """测试文件验证"""
        # 测试有效文件
        valid_content = b"fake image content"
        valid_type = "image/jpeg"
        
        validation_result = cos_service.validate_file(valid_content, valid_type)
        self.assertTrue(validation_result['valid'])
        self.assertEqual(validation_result['error'], '')
        
        # 测试文件类型验证
        invalid_type = "application/pdf"
        validation_result = cos_service.validate_file(valid_content, invalid_type)
        self.assertFalse(validation_result['valid'])
        self.assertIn('不支持的文件类型', validation_result['error'])
        
        # 测试文件大小验证
        oversized_content = b"x" * (10 * 1024 * 1024)  # 10MB
        validation_result = cos_service.validate_file(oversized_content, valid_type)
        self.assertFalse(validation_result['valid'])
        self.assertIn('文件大小不能超过', validation_result['error'])