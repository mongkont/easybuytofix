#!/usr/bin/env python
"""
Script to manage Cloudflare R2 files
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
import boto3
from botocore.exceptions import ClientError

def list_r2_files(prefix=''):
    """List all files in R2 bucket"""
    if not getattr(settings, 'R2_ENABLED', False):
        print("R2 is not enabled")
        return
    
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix=prefix
        )
        
        if 'Contents' in response:
            print(f"Files in bucket '{settings.AWS_STORAGE_BUCKET_NAME}':")
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("No files found")
            
    except Exception as e:
        print(f"Error listing files: {e}")

def delete_r2_file(file_path):
    """Delete a file from R2"""
    if not getattr(settings, 'R2_ENABLED', False):
        print("R2 is not enabled")
        return
    
    try:
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            print(f"✅ Deleted: {file_path}")
        else:
            print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")

def upload_file_to_r2(local_file_path, r2_file_path=None):
    """Upload a local file to R2"""
    if not getattr(settings, 'R2_ENABLED', False):
        print("R2 is not enabled")
        return
    
    try:
        if not os.path.exists(local_file_path):
            print(f"❌ Local file not found: {local_file_path}")
            return
        
        if r2_file_path is None:
            r2_file_path = os.path.basename(local_file_path)
        
        with open(local_file_path, 'rb') as f:
            saved_path = default_storage.save(r2_file_path, f)
            file_url = default_storage.url(saved_path)
            print(f"✅ Uploaded: {local_file_path} -> {saved_path}")
            print(f"   URL: {file_url}")
            
    except Exception as e:
        print(f"Error uploading file: {e}")

def get_file_url(file_path):
    """Get URL of a file in R2"""
    if not getattr(settings, 'R2_ENABLED', False):
        print("R2 is not enabled")
        return
    
    try:
        if default_storage.exists(file_path):
            file_url = default_storage.url(file_path)
            print(f"URL for {file_path}: {file_url}")
        else:
            print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"Error getting file URL: {e}")

def show_r2_info():
    """Show R2 configuration info"""
    print("Cloudflare R2 Configuration:")
    print(f"  Enabled: {getattr(settings, 'R2_ENABLED', False)}")
    print(f"  Bucket: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
    print(f"  Endpoint: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'Not set')}")
    print(f"  Custom Domain: {getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'Not set')}")
    print(f"  Media URL: {getattr(settings, 'MEDIA_URL', 'Not set')}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_r2.py info                    - Show R2 info")
        print("  python manage_r2.py list [prefix]           - List files")
        print("  python manage_r2.py upload <local> [remote] - Upload file")
        print("  python manage_r2.py delete <file_path>      - Delete file")
        print("  python manage_r2.py url <file_path>         - Get file URL")
        return
    
    command = sys.argv[1]
    
    if command == 'info':
        show_r2_info()
    elif command == 'list':
        prefix = sys.argv[2] if len(sys.argv) > 2 else ''
        list_r2_files(prefix)
    elif command == 'upload':
        if len(sys.argv) < 3:
            print("Please provide local file path")
            return
        local_path = sys.argv[2]
        remote_path = sys.argv[3] if len(sys.argv) > 3 else None
        upload_file_to_r2(local_path, remote_path)
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("Please provide file path to delete")
            return
        file_path = sys.argv[2]
        delete_r2_file(file_path)
    elif command == 'url':
        if len(sys.argv) < 3:
            print("Please provide file path")
            return
        file_path = sys.argv[2]
        get_file_url(file_path)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
