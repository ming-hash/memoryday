#!/usr/bin/env python3
"""
MemoryDay Environment Configuration Check Tool
This script validates the environment configuration for the MemoryDay backend.
"""

import os
import sys
import django
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memoryday_backend.settings')
django.setup()

from django.conf import settings
from apps.cos.services import COSService


class EnvironmentChecker:
    """Environment configuration checker for MemoryDay backend"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def log_error(self, message):
        """Log an error message"""
        self.errors.append(f"❌ {message}")
        print(f"❌ {message}")
        
    def log_warning(self, message):
        """Log a warning message"""
        self.warnings.append(f"⚠️ {message}")
        print(f"⚠️ {message}")
        
    def log_success(self, message):
        """Log a success message"""
        self.successes.append(f"✅ {message}")
        print(f"✅ {message}")
        
    def check_django_settings(self):
        """Check Django settings configuration"""
        print("\n🔍 Checking Django settings...")
        
        # Check DEBUG mode
        if settings.DEBUG:
            self.log_warning("DEBUG mode is enabled. Disable in production.")
        else:
            self.log_success("DEBUG mode is disabled (production ready)")
            
        # Check SECRET_KEY
        if not settings.SECRET_KEY or settings.SECRET_KEY == 'your-secret-key-here':
            self.log_error("SECRET_KEY is not properly configured")
        else:
            self.log_success("SECRET_KEY is configured")
            
        # Check ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS:
            self.log_error("ALLOWED_HOSTS is empty")
        else:
            self.log_success(f"ALLOWED_HOSTS configured: {settings.ALLOWED_HOSTS}")
            
        # Check database configuration
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'sqlite' in db_engine and not settings.DEBUG:
            self.log_error("SQLite database in production is not recommended")
        else:
            self.log_success(f"Database engine: {db_engine}")
            
    def check_cos_configuration(self):
        """Check Tencent Cloud COS configuration"""
        print("\n🔍 Checking COS configuration...")
        
        cos_config = getattr(settings, 'COS_CONFIG', {})
        
        # Check if COS is enabled
        if not cos_config.get('enabled', False):
            self.log_warning("COS is not enabled")
            return
            
        self.log_success("COS is enabled")
        
        # Check required COS parameters
        required_params = ['secret_id', 'secret_key', 'bucket', 'region']
        for param in required_params:
            if not cos_config.get(param):
                self.log_error(f"COS {param} is not configured")
            else:
                # Mask sensitive values for logging
                if param in ['secret_id', 'secret_key']:
                    value = cos_config[param][:4] + '***' + cos_config[param][-4:]
                else:
                    value = cos_config[param]
                self.log_success(f"COS {param}: {value}")
                
        # Test COS service connection
        try:
            cos_service = COSService()
            # Simple test to check if configuration is valid
            if cos_service.check_configuration():
                self.log_success("COS service configuration is valid")
            else:
                self.log_error("COS service configuration test failed")
        except Exception as e:
            self.log_error(f"COS service test failed: {str(e)}")
            
    def check_database_connection(self):
        """Check database connection"""
        print("\n🔍 Checking database connection...")
        
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    self.log_success("Database connection successful")
                else:
                    self.log_error("Database connection test failed")
        except Exception as e:
            self.log_error(f"Database connection failed: {str(e)}")
            
    def check_redis_connection(self):
        """Check Redis connection"""
        print("\n🔍 Checking Redis connection...")
        
        redis_url = getattr(settings, 'REDIS_URL', None)
        if not redis_url:
            self.log_warning("Redis configuration not found")
            return
            
        try:
            import redis
            redis_client = redis.from_url(redis_url)
            redis_client.ping()
            self.log_success("Redis connection successful")
        except Exception as e:
            self.log_error(f"Redis connection failed: {str(e)}")
            
    def check_environment_variables(self):
        """Check environment variables"""
        print("\n🔍 Checking environment variables...")
        
        required_vars = [
            'DJANGO_SECRET_KEY',
            'MYSQL_DATABASE', 
            'MYSQL_USER',
            'MYSQL_PASSWORD',
            'MYSQL_HOST',
            'REDIS_URL'
        ]
        
        optional_vars = [
            'COS_ENABLED',
            'COS_SECRET_ID', 
            'COS_SECRET_KEY',
            'COS_BUCKET',
            'COS_REGION',
            'WECHAT_APPID',
            'WECHAT_SECRET'
        ]
        
        # Check required variables
        for var in required_vars:
            if not os.getenv(var):
                self.log_error(f"Required environment variable {var} is not set")
            else:
                self.log_success(f"{var} is set")
                
        # Check optional variables
        for var in optional_vars:
            if not os.getenv(var):
                self.log_warning(f"Optional environment variable {var} is not set")
            else:
                self.log_success(f"{var} is set")
                
    def check_file_permissions(self):
        """Check file and directory permissions"""
        print("\n🔍 Checking file permissions...")
        
        directories_to_check = [
            project_root / 'logs',
            project_root / 'static',
            project_root / 'media',
            project_root / '.env'
        ]
        
        for directory in directories_to_check:
            if directory.exists():
                try:
                    # Test if we can read the directory/file
                    if directory.is_dir():
                        list(directory.iterdir())
                        self.log_success(f"Directory {directory} is accessible")
                    else:
                        directory.read_text()
                        self.log_success(f"File {directory} is accessible")
                except Exception as e:
                    self.log_error(f"Cannot access {directory}: {str(e)}")
            else:
                self.log_warning(f"{directory} does not exist")
                
    def check_api_endpoints(self):
        """Check API endpoints"""
        print("\n🔍 Checking API endpoints...")
        
        base_url = "http://localhost:8000"
        endpoints = [
            "/api/health/",
            "/api/cos/status/",
            "/api/cos/sts/"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_success(f"API endpoint {endpoint} is accessible")
                else:
                    self.log_warning(f"API endpoint {endpoint} returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_error(f"API endpoint {endpoint} is not accessible: {str(e)}")
                
    def generate_report(self):
        """Generate a summary report"""
        print("\n" + "="*60)
        print("📊 ENVIRONMENT CHECK REPORT")
        print("="*60)
        
        print(f"\n✅ Successes: {len(self.successes)}")
        for success in self.successes:
            print(f"   {success}")
            
        print(f"\n⚠️ Warnings: {len(self.warnings)}")
        for warning in self.warnings:
            print(f"   {warning}")
            
        print(f"\n❌ Errors: {len(self.errors)}")
        for error in self.errors:
            print(f"   {error}")
            
        # Overall status
        if self.errors:
            print(f"\n🔴 Status: CRITICAL - {len(self.errors)} errors need to be fixed")
            return 1
        elif self.warnings:
            print(f"\n🟡 Status: WARNING - {len(self.warnings)} warnings to review")
            return 0
        else:
            print(f"\n🟢 Status: SUCCESS - Environment is properly configured")
            return 0
            
    def run_all_checks(self):
        """Run all environment checks"""
        print("🚀 Starting MemoryDay Environment Check...")
        print("="*60)
        
        self.check_environment_variables()
        self.check_django_settings()
        self.check_cos_configuration()
        self.check_database_connection()
        self.check_redis_connection()
        self.check_file_permissions()
        self.check_api_endpoints()
        
        return self.generate_report()


def main():
    """Main function"""
    checker = EnvironmentChecker()
    exit_code = checker.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()