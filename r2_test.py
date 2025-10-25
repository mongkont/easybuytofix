#!/usr/bin/env python
"""
Script to test Cloudflare R2 connection and file upload
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easybuytofix.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

def test_r2_connection():
    """Test R2 connection and file upload"""
    print("Testing Cloudflare R2 connection...")
    print(f"R2 Enabled: {getattr(settings, 'R2_ENABLED', False)}")
    
    if not getattr(settings, 'R2_ENABLED', False):
        print("R2 is not enabled. Please set R2_ENABLED=True in .env file")
        return False
    
    try:
        # Test file content
        test_content = "This is a test file for R2 upload"
        test_file = ContentFile(test_content.encode())
        
        # Upload test file
        file_path = "test/test_file.txt"
        saved_path = default_storage.save(file_path, test_file)
        
        print(f"✅ File uploaded successfully: {saved_path}")
        
        # Check if file exists
        if default_storage.exists(saved_path):
            print("✅ File exists in R2")
            
            # Get file URL
            file_url = default_storage.url(saved_path)
            print(f"✅ File URL: {file_url}")
            
            # Read file content
            with default_storage.open(saved_path, 'r') as f:
                content = f.read()
                print(f"✅ File content: {content}")
            
            # Delete test file
            default_storage.delete(saved_path)
            print("✅ Test file deleted")
            
            return True
        else:
            print("❌ File does not exist in R2")
            return False
            
    except Exception as e:
        print(f"❌ Error testing R2: {e}")
        return False

def show_r2_config():
    """Show current R2 configuration"""
    print("\nCurrent R2 Configuration:")
    print(f"R2_ENABLED: {getattr(settings, 'R2_ENABLED', False)}")
    print(f"AWS_ACCESS_KEY_ID: {getattr(settings, 'AWS_ACCESS_KEY_ID', 'Not set')}")
    print(f"AWS_SECRET_ACCESS_KEY: {'*' * 10 if getattr(settings, 'AWS_SECRET_ACCESS_KEY', None) else 'Not set'}")
    print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
    print(f"AWS_S3_ENDPOINT_URL: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'Not set')}")
    print(f"AWS_S3_CUSTOM_DOMAIN: {getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'Not set')}")
    print(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'Not set')}")

if __name__ == "__main__":
    show_r2_config()
    print("\n" + "="*50)
    test_r2_connection()
