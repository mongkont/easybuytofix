from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from .models import UserProfile
import os


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(
            user=instance,
            created_by=instance
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(pre_delete, sender=UserProfile)
def delete_user_avatar(sender, instance, **kwargs):
    """Delete avatar file when UserProfile is deleted"""
    if instance.avatar:
        try:
            # Delete from storage (works for both local and R2)
            if default_storage.exists(instance.avatar.name):
                default_storage.delete(instance.avatar.name)
        except Exception as e:
            # Log error but don't prevent deletion
            print(f"Error deleting avatar: {e}")


@receiver(post_save, sender=UserProfile)
def delete_old_avatar_on_update(sender, instance, created, **kwargs):
    """Delete old avatar when updating to new one and fix permissions"""
    if not created and instance.avatar:
        try:
            # Get the old instance from database
            old_instance = UserProfile.objects.get(pk=instance.pk)
            if old_instance.avatar and old_instance.avatar != instance.avatar:
                # Delete old avatar file
                if default_storage.exists(old_instance.avatar.name):
                    default_storage.delete(old_instance.avatar.name)
                    print(f"✅ ลบรูปเก่าอัตโนมัติ: {old_instance.avatar.name}")
        except UserProfile.DoesNotExist:
            pass
        except Exception as e:
            # Log error but don't prevent save
            print(f"❌ Error deleting old avatar: {e}")
    
    # Fix permissions for new avatar
    if instance.avatar and instance.avatar.name:
        try:
            import boto3
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            # Create S3 client for R2
            s3_client = boto3.client(
                's3',
                endpoint_url=os.getenv('R2_ENDPOINT_URL'),
                aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
            )
            
            bucket_name = os.getenv('R2_BUCKET_NAME')
            
            # Get file content
            file_content = default_storage.open(instance.avatar.name).read()
            
            # Determine content type
            content_type = 'image/jpeg'
            if instance.avatar.name.lower().endswith('.png'):
                content_type = 'image/png'
            elif instance.avatar.name.lower().endswith('.gif'):
                content_type = 'image/gif'
            elif instance.avatar.name.lower().endswith('.webp'):
                content_type = 'image/webp'
            
            # Upload with public-read ACL
            s3_client.put_object(
                Bucket=bucket_name,
                Key=instance.avatar.name,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'
            )
            
            print(f"✅ Avatar permissions fixed automatically: {instance.avatar.name}")
            
        except Exception as e:
            # Log error but don't prevent save
            print(f"Error fixing avatar permissions: {e}")
