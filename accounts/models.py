from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


def user_avatar_upload_path(instance, filename):
    """Generate upload path for user avatar"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Create filename with user ID and timestamp
    filename = f"avatars/user_{instance.user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return filename


class UserProfile(models.Model):
    """User Profile model with avatar and additional information"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='ผู้ใช้'
    )
    
    avatar = models.ImageField(
        upload_to=user_avatar_upload_path,
        blank=True,
        null=True,
        verbose_name='รูปโปรไฟล์',
        help_text='อัปโหลดรูปโปรไฟล์ของคุณ'
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='เบอร์โทรศัพท์',
        help_text='เบอร์โทรศัพท์ติดต่อ'
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='ข้อมูลส่วนตัว',
        help_text='ข้อมูลเพิ่มเติมเกี่ยวกับคุณ'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='วันเกิด'
    )
    
    address = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='ที่อยู่'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='วันที่สร้าง'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='วันที่แก้ไข'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_profiles',
        verbose_name='ผู้สร้าง'
    )
    
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_profiles',
        verbose_name='ผู้แก้ไข'
    )
    
    class Meta:
        verbose_name = 'โปรไฟล์ผู้ใช้'
        verbose_name_plural = 'โปรไฟล์ผู้ใช้'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Profile of {self.user.get_full_name() or self.user.username}"
    
    @property
    def full_name(self):
        """Get user's full name"""
        return self.user.get_full_name() or self.user.username
    
    @property
    def avatar_url(self):
        """Get avatar URL"""
        if self.avatar:
            return self.avatar.url
        return None
    
    def save(self, *args, **kwargs):
        # Set created_by and updated_by if not set
        if not self.pk and not self.created_by:
            # This is a new profile, set created_by to the user
            self.created_by = self.user
        
        super().save(*args, **kwargs)
    
    def delete_old_avatar(self):
        """Delete old avatar file when updating"""
        if self.avatar:
            try:
                if os.path.isfile(self.avatar.path):
                    os.remove(self.avatar.path)
            except (ValueError, OSError):
                # File might be on cloud storage (R2)
                pass