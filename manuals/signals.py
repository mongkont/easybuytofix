from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from .models import Manual, ManualAttachment
import os
from dotenv import load_dotenv
import boto3
import re

load_dotenv()


@receiver(post_delete, sender=Manual)
def delete_manual_attachments_on_delete(sender, instance, **kwargs):
    """Delete manual attachments when Manual is deleted"""
    # Find all attachments referenced in the content
    if instance.content:
        # Extract image URLs from content
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        img_urls = re.findall(img_pattern, instance.content)
        
        for img_url in img_urls:
            # Extract file path from URL
            if '/manuals/images/' in img_url:
                file_path = img_url.split('/manuals/images/')[-1]
                full_path = f'manuals/images/{file_path}'
                
                try:
                    if default_storage.exists(full_path):
                        default_storage.delete(full_path)
                        print(f"✅ ลบไฟล์แนบคู่มือ: {full_path}")
                except Exception as e:
                    print(f"❌ Error deleting manual attachment {full_path}: {e}")


@receiver(post_save, sender=ManualAttachment)
def fix_manual_attachment_permissions(sender, instance, created, **kwargs):
    """Fix permissions for manual attachments uploaded via Summernote"""
    if created and instance.file:
        try:
            import boto3
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            r2_enabled = os.getenv('R2_ENABLED', 'False').lower() == 'true'
            if not r2_enabled:
                return
            
            # Create S3 client for R2
            s3_client = boto3.client(
                's3',
                endpoint_url=os.getenv('R2_ENDPOINT_URL'),
                aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
            )
            
            bucket_name = os.getenv('R2_BUCKET_NAME')
            
            # Get file content
            with default_storage.open(instance.file.name, 'rb') as f:
                file_content = f.read()
            
            # Determine content type
            content_type = 'application/octet-stream'
            if instance.file.name.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif instance.file.name.lower().endswith('.png'):
                content_type = 'image/png'
            elif instance.file.name.lower().endswith('.gif'):
                content_type = 'image/gif'
            elif instance.file.name.lower().endswith('.webp'):
                content_type = 'image/webp'
            
            # Upload with public-read ACL
            s3_client.put_object(
                Bucket=bucket_name,
                Key=instance.file.name,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'
            )
            
            print(f"✅ Manual attachment permissions fixed: {instance.file.name}")
            
        except Exception as e:
            print(f"❌ Error fixing manual attachment permissions: {e}")


@receiver(post_delete, sender=ManualAttachment)
def delete_manual_attachment_file(sender, instance, **kwargs):
    """Delete attachment file when ManualAttachment is deleted"""
    if instance.file:
        try:
            if default_storage.exists(instance.file.name):
                default_storage.delete(instance.file.name)
                print(f"✅ ลบไฟล์แนบคู่มือ: {instance.file.name}")
        except Exception as e:
            print(f"❌ Error deleting manual attachment file: {e}")


@receiver(post_save, sender=Manual)
def cleanup_orphaned_attachments(sender, instance, created, **kwargs):
    """Clean up orphaned attachments when manual content is updated"""
    if not created and instance.content:
        try:
            # Get old content from database
            old_instance = Manual.objects.get(pk=instance.pk)
            if old_instance.content != instance.content:
                # Extract old image URLs
                old_img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
                old_img_urls = re.findall(old_img_pattern, old_instance.content)
                
                # Extract new image URLs
                new_img_urls = re.findall(old_img_pattern, instance.content)
                
                # Find orphaned images
                orphaned_urls = set(old_img_urls) - set(new_img_urls)
                
                for img_url in orphaned_urls:
                    if '/manuals/images/' in img_url:
                        file_path = img_url.split('/manuals/images/')[-1]
                        full_path = f'manuals/images/{file_path}'
                        
                        try:
                            if default_storage.exists(full_path):
                                default_storage.delete(full_path)
                                print(f"✅ ลบไฟล์แนบที่ไม่ได้ใช้: {full_path}")
                        except Exception as e:
                            print(f"❌ Error deleting orphaned attachment {full_path}: {e}")
                            
        except Manual.DoesNotExist:
            pass
        except Exception as e:
            print(f"❌ Error cleaning up orphaned attachments: {e}")
