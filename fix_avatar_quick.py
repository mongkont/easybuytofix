#!/usr/bin/env python
"""
Quick script to fix avatar permissions for current user
"""
import boto3
import os
import django
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup Django first
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easybuytofix.settings')
django.setup()

from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from accounts.models import UserProfile

load_dotenv()

def fix_current_user_avatar():
    """Fix avatar permissions for current user"""
    
    try:
        # Get current user (mongkont)
        user = User.objects.get(username='mongkont')
        profile = user.profile
        
        if not profile.avatar:
            print("❌ No avatar found for user")
            return False
        
        print(f"Fixing avatar for user: {user.username}")
        print(f"Avatar path: {profile.avatar.name}")
        
        # Create S3 client for R2
        s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('R2_ENDPOINT_URL'),
            aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
        )
        
        bucket_name = os.getenv('R2_BUCKET_NAME')
        
        # Check if file exists in storage
        if default_storage.exists(profile.avatar.name):
            # Get file content
            file_content = default_storage.open(profile.avatar.name).read()
            
            # Determine content type
            content_type = 'image/jpeg'
            if profile.avatar.name.lower().endswith('.png'):
                content_type = 'image/png'
            elif profile.avatar.name.lower().endswith('.gif'):
                content_type = 'image/gif'
            elif profile.avatar.name.lower().endswith('.webp'):
                content_type = 'image/webp'
            
            # Upload with public-read ACL
            s3_client.put_object(
                Bucket=bucket_name,
                Key=profile.avatar.name,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'
            )
            
            print("✅ Avatar permissions fixed!")
            print(f"🌐 Public URL: {profile.avatar_url}")
            
            # Test URL
            import requests
            try:
                response = requests.head(profile.avatar_url)
                if response.status_code == 200:
                    print("✅ Avatar is publicly accessible!")
                else:
                    print(f"❌ Avatar still not accessible (Status: {response.status_code})")
            except Exception as e:
                print(f"❌ Error testing URL: {e}")
            
            return True
        else:
            print("❌ Avatar file not found in storage")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Quick Avatar Permission Fix")
    print("=" * 40)
    success = fix_current_user_avatar()
    
    if success:
        print("\n🎉 Avatar permissions fixed successfully!")
    else:
        print("\n❌ Failed to fix avatar permissions.")
