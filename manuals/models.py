from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django_summernote.models import AbstractAttachment
import re
from unidecode import unidecode

User = get_user_model()


def custom_slugify(value):
    """Create slug that supports Thai characters"""
    if not value:
        return ''
    
    # Use unidecode to convert Thai to readable text
    decoded = unidecode(value)
    
    # Clean up the result
    result = re.sub(r'[^\w\s-]', '', decoded)  # Remove special characters
    result = re.sub(r'[-\s]+', '-', result)    # Replace spaces and multiple dashes with single dash
    result = result.strip('-')                 # Remove leading/trailing dashes
    
    return result.lower()


class ManualCategory(models.Model):
    """Manual Category model"""
    name = models.CharField(
        _("ชื่อหมวดหมู่"),
        max_length=100,
        unique=True,
        help_text=_("ชื่อหมวดหมู่คู่มือการใช้งาน")
    )
    slug = models.CharField(
        _("Slug"),
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("URL-friendly version of the name (auto-generated or manual)")
    )
    description = models.TextField(
        _("รายละเอียด"),
        blank=True,
        null=True,
        help_text=_("รายละเอียดเพิ่มเติมเกี่ยวกับหมวดหมู่")
    )
    icon = models.CharField(
        _("ไอคอน"),
        max_length=50,
        blank=True,
        help_text=_("Font Awesome class เช่น 'fas fa-book'")
    )
    order = models.IntegerField(
        _("ลำดับ"),
        default=0,
        help_text=_("ลำดับการแสดงผล (น้อยกว่า = แสดงก่อน)")
    )
    is_active = models.BooleanField(
        _("ใช้งานได้"),
        default=True,
        help_text=_("สถานะการใช้งานของหมวดหมู่")
    )
    created_at = models.DateTimeField(
        _("วันที่สร้าง"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("วันที่แก้ไข"),
        auto_now=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_manual_categories',
        blank=True,
        null=True,
        verbose_name=_("ผู้สร้าง")
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='updated_manual_categories',
        blank=True,
        null=True,
        verbose_name=_("ผู้แก้ไข")
    )

    class Meta:
        verbose_name = _("หมวดหมู่คู่มือ")
        verbose_name_plural = _("หมวดหมู่คู่มือ")
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = custom_slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while ManualCategory.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class Manual(models.Model):
    """Manual model"""
    title = models.CharField(
        _("ชื่อคู่มือ"),
        max_length=200,
        help_text=_("ชื่อคู่มือการใช้งาน")
    )
    category = models.ForeignKey(
        ManualCategory,
        on_delete=models.CASCADE,
        related_name='manuals',
        verbose_name=_("หมวดหมู่")
    )
    slug = models.CharField(
        _("Slug"),
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("URL-friendly version of the title (auto-generated or manual)")
    )
    content = models.TextField(
        _("รายละเอียด"),
        help_text=_("เนื้อหาคู่มือการใช้งาน (ใช้ Summernote Editor)")
    )
    
    # Visibility settings
    is_public = models.BooleanField(
        _("สาธารณะ"),
        default=False,
        help_text=_("แสดงสำหรับทุกคน")
    )
    visible_to_groups = models.ManyToManyField(
        Group,
        blank=True,
        verbose_name=_("แสดงสำหรับกลุ่ม"),
        help_text=_("เลือกกลุ่มที่สามารถเห็นคู่มือนี้")
    )
    
    # Ordering - Simple order field
    order = models.PositiveIntegerField(
        _("ลำดับ"),
        default=0,
        help_text=_("ลำดับการแสดงผล (ตัวเลขน้อย = แสดงก่อน)")
    )
    
    # SEO
    seo_title = models.CharField(
        _("SEO Title"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("ชื่อหน้าเว็บสำหรับ SEO (แนะนำไม่เกิน 100 ตัวอักษร)")
    )
    seo_description = models.TextField(
        _("SEO Description"),
        blank=True,
        null=True,
        help_text=_("คำอธิบายสำหรับ SEO (แนะนำไม่เกิน 200 ตัวอักษร)")
    )
    
    is_active = models.BooleanField(
        _("ใช้งานได้"),
        default=True,
        help_text=_("สถานะการใช้งานของคู่มือ")
    )
    created_at = models.DateTimeField(
        _("วันที่สร้าง"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("วันที่แก้ไข"),
        auto_now=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_manuals',
        blank=True,
        null=True,
        verbose_name=_("ผู้สร้าง")
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='updated_manuals',
        blank=True,
        null=True,
        verbose_name=_("ผู้แก้ไข")
    )

    class Meta:
        verbose_name = _("คู่มือการใช้งาน")
        verbose_name_plural = _("คู่มือการใช้งาน")
        ordering = ['category__order', 'category__name', 'order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided"""
        if not self.slug:
            self.slug = custom_slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Manual.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def calculated_order(self):
        """Calculate position based on order_before"""
        if self.order_before:
            # Get all manuals in the same category
            category_manuals = Manual.objects.filter(category=self.category, is_active=True).exclude(pk=self.pk)
            
            # Find position of the manual we want to be before
            before_manual = self.order_before
            if before_manual in category_manuals:
                # Count manuals before the target manual
                count_before = category_manuals.filter(
                    models.Q(calculated_order__lt=before_manual.calculated_order) |
                    models.Q(order_before__isnull=True, pk__lt=before_manual.pk)
                ).count()
                return count_before
        return 999  # Default to end

    @property
    def seo_title_display(self):
        """Get SEO title or fallback to title"""
        return self.seo_title if self.seo_title else self.title


class ManualAttachment(AbstractAttachment):
    """Manual Attachment model for Summernote uploads"""
    
    class Meta:
        verbose_name = _("ไฟล์แนบคู่มือ")
        verbose_name_plural = _("ไฟล์แนบคู่มือ")
        ordering = ['-id']

    def __str__(self):
        return self.name or self.file.name

    def save(self, *args, **kwargs):
        """Set name from file if not provided"""
        if not self.name and self.file:
            self.name = self.file.name.split('/')[-1]
        super().save(*args, **kwargs)