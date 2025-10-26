from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from .models import Category, Brand


@receiver(post_delete, sender=Category)
def delete_category_images_on_delete(sender, instance, **kwargs):
    """Delete category images when Category is deleted"""
    if instance.image:
        if default_storage.exists(instance.image.name):
            default_storage.delete(instance.image.name)
            print(f"✅ ลบรูปหมวดหมู่: {instance.image.name}")
    
    if instance.og_image:
        if default_storage.exists(instance.og_image.name):
            default_storage.delete(instance.og_image.name)
            print(f"✅ ลบรูป OG: {instance.og_image.name}")


@receiver(post_save, sender=Category)
def delete_old_category_images_on_update(sender, instance, created, **kwargs):
    """Delete old category images when updating to new ones and fix permissions"""
    if not created:
        try:
            # Get the old instance from database
            old_instance = Category.objects.get(pk=instance.pk)
            
            # Delete old main image if changed
            if old_instance.image and old_instance.image != instance.image:
                if default_storage.exists(old_instance.image.name):
                    default_storage.delete(old_instance.image.name)
                    print(f"✅ ลบรูปเก่าอัตโนมัติ: {old_instance.image.name}")
            
            # Delete old OG image if changed
            if old_instance.og_image and old_instance.og_image != instance.og_image:
                if default_storage.exists(old_instance.og_image.name):
                    default_storage.delete(old_instance.og_image.name)
                    print(f"✅ ลบรูป OG เก่าอัตโนมัติ: {old_instance.og_image.name}")
                    
        except Category.DoesNotExist:
            pass
        except Exception as e:
            print(f"❌ Error deleting old images: {e}")
    
    # Fix permissions for new images
    for image_field in [instance.image, instance.og_image]:
        if image_field and image_field.name:
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
                with default_storage.open(image_field.name, 'rb') as f:
                    file_content = f.read()
                
                # Determine content type
                content_type = 'application/octet-stream'
                if image_field.name.lower().endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif image_field.name.lower().endswith('.png'):
                    content_type = 'image/png'
                elif image_field.name.lower().endswith('.gif'):
                    content_type = 'image/gif'
                elif image_field.name.lower().endswith('.webp'):
                    content_type = 'image/webp'
                
                # Upload with public-read ACL
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=image_field.name,
                    Body=file_content,
                    ContentType=content_type,
                    ACL='public-read'
                )
                
                print(f"✅ รูปหมวดหมู่ permissions fixed: {image_field.name}")
                
            except Exception as e:
                print(f"❌ Error fixing image permissions: {e}")


# Brand signals
@receiver(post_delete, sender=Brand)
def delete_brand_logos_on_delete(sender, instance, **kwargs):
    """Delete brand logos when Brand is deleted"""
    if instance.logo:
        if default_storage.exists(instance.logo.name):
            default_storage.delete(instance.logo.name)
            print(f"✅ ลบโลโก้แบรนด์: {instance.logo.name}")
    
    if instance.og_image:
        if default_storage.exists(instance.og_image.name):
            default_storage.delete(instance.og_image.name)
            print(f"✅ ลบรูป OG แบรนด์: {instance.og_image.name}")


@receiver(post_save, sender=Brand)
def delete_old_brand_logos_on_update(sender, instance, created, **kwargs):
    """Delete old brand logos when updating to new ones and fix permissions"""
    if not created:
        try:
            # Get the old instance from database
            old_instance = Brand.objects.get(pk=instance.pk)
            
            # Delete old main logo if changed
            if old_instance.logo and old_instance.logo != instance.logo:
                if default_storage.exists(old_instance.logo.name):
                    default_storage.delete(old_instance.logo.name)
                    print(f"✅ ลบโลโก้เก่าอัตโนมัติ: {old_instance.logo.name}")
            
            # Delete old OG image if changed
            if old_instance.og_image and old_instance.og_image != instance.og_image:
                if default_storage.exists(old_instance.og_image.name):
                    default_storage.delete(old_instance.og_image.name)
                    print(f"✅ ลบรูป OG เก่าอัตโนมัติ: {old_instance.og_image.name}")
                    
        except Brand.DoesNotExist:
            pass
        except Exception as e:
            print(f"❌ Error deleting old brand logos: {e}")
    
    # Fix permissions for new images
    for image_field in [instance.logo, instance.og_image]:
        if image_field and image_field.name:
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
                with default_storage.open(image_field.name, 'rb') as f:
                    file_content = f.read()
                
                # Determine content type
                content_type = 'application/octet-stream'
                if image_field.name.lower().endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif image_field.name.lower().endswith('.png'):
                    content_type = 'image/png'
                elif image_field.name.lower().endswith('.gif'):
                    content_type = 'image/gif'
                elif image_field.name.lower().endswith('.webp'):
                    content_type = 'image/webp'
                
                # Upload with public-read ACL
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=image_field.name,
                    Body=file_content,
                    ContentType=content_type,
                    ACL='public-read'
                )
                
                print(f"✅ โลโก้แบรนด์ permissions fixed: {image_field.name}")
                
            except Exception as e:
                print(f"❌ Error fixing brand logo permissions: {e}")
