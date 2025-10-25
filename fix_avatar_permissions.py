#!/usr/bin/env python
"""
Script to fix avatar permissions in R2
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

def fix_avatar_permissions():
    """Fix avatar permissions in R2"""
    
    # Create S3 client for R2
    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv('R2_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
    )
    
    bucket_name = os.getenv('R2_BUCKET_NAME')
    
    try:
        # Get all profiles with avatars
        profiles = UserProfile.objects.filter(avatar__isnull=False)
        
        print(f"Found {profiles.count()} profiles with avatars")
        
        for profile in profiles:
            if profile.avatar and profile.avatar.name:
                print(f"Processing avatar for user: {profile.user.username}")
                print(f"Avatar path: {profile.avatar.name}")
                
                # Check if file exists in storage
                if default_storage.exists(profile.avatar.name):
                    # Get file content
                    file_content = default_storage.open(profile.avatar.name).read()
                    
                    # Upload with public-read ACL
                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=profile.avatar.name,
                        Body=file_content,
                        ContentType='image/jpeg',
                        ACL='public-read'
                    )
                    
                    print(f"✅ Fixed permissions for: {profile.avatar.name}")
                    print(f"🌐 Public URL: {profile.avatar_url}")
                else:
                    print(f"❌ File not found: {profile.avatar.name}")
                
                print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing permissions: {e}")
        return False

if __name__ == "__main__":
    print("Fixing avatar permissions in R2...")
    success = fix_avatar_permissions()
    
    if success:
        print("\n🎉 Avatar permissions fixed!")
        print("All avatars should now be publicly accessible.")
    else:
        print("\n❌ Failed to fix permissions.")
