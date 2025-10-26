from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import os
from datetime import datetime

User = get_user_model()


def category_image_upload_path(instance, filename):
    """Generate upload path for category images"""
    ext = filename.split('.')[-1]
    filename = f"category_{instance.pk}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('categories', filename)


class Category(models.Model):
    """Product category model"""
    name = models.CharField(
        _("ชื่อหมวดหมู่"),
        max_length=100,
        unique=True,
        help_text=_("ชื่อหมวดหมู่สินค้า")
    )
    description = models.TextField(
        _("รายละเอียดหมวดหมู่"),
        blank=True,
        null=True,
        help_text=_("รายละเอียดเพิ่มเติมเกี่ยวกับหมวดหมู่สินค้า")
    )
    image = models.ImageField(
        _("รูปหมวดหมู่"),
        upload_to=category_image_upload_path,
        blank=True,
        null=True,
        help_text=_("อัปโหลดรูปหมวดหมู่สินค้า (ขนาด 1:1)")
    )
    is_active = models.BooleanField(
        _("ใช้งานได้"),
        default=True,
        help_text=_("หมวดหมู่นี้ใช้งานได้หรือไม่")
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
        related_name='created_categories',
        blank=True,
        null=True,
        verbose_name=_("ผู้สร้าง")
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='updated_categories',
        blank=True,
        null=True,
        verbose_name=_("ผู้แก้ไข")
    )
    
    # SEO Fields
    seo_title = models.CharField(
        _("SEO Title"),
        max_length=60,
        blank=True,
        null=True,
        help_text=_("ชื่อหน้าเว็บสำหรับ SEO (แนะนำไม่เกิน 60 ตัวอักษร)")
    )
    seo_description = models.TextField(
        _("SEO Description"),
        max_length=160,
        blank=True,
        null=True,
        help_text=_("คำอธิบายสำหรับ SEO (แนะนำไม่เกิน 160 ตัวอักษร)")
    )
    alt_text = models.CharField(
        _("Alt Text"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("ข้อความอธิบายรูปสำหรับผู้ใช้ที่มองไม่เห็น")
    )
    
    # OG (Open Graph) Fields
    og_image = models.ImageField(
        _("OG Image"),
        upload_to=category_image_upload_path,
        blank=True,
        null=True,
        help_text=_("รูปสำหรับแชร์ใน Social Media (ขนาด 1200x630px - อัตราส่วน 16:9)")
    )
    og_title = models.CharField(
        _("OG Title"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("ชื่อสำหรับแชร์ใน Social Media (แนะนำไม่เกิน 100 ตัวอักษร เพื่อความเหมาะสมในทุกแพลตฟอร์ม)")
    )
    og_description = models.TextField(
        _("OG Description"),
        blank=True,
        null=True,
        help_text=_("คำอธิบายสำหรับแชร์ใน Social Media (แนะนำไม่เกิน 200 ตัวอักษร เพื่อความเหมาะสมในทุกแพลตฟอร์ม)")
    )

    class Meta:
        verbose_name = _("หมวดหมู่สินค้า")
        verbose_name_plural = _("หมวดหมู่สินค้า")
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def image_size(self):
        """Get image dimensions if available"""
        if self.image:
            try:
                from PIL import Image
                with self.image.open() as img:
                    pil_img = Image.open(img)
                    return f"{pil_img.width}x{pil_img.height}"
            except:
                return "ไม่สามารถอ่านขนาดได้"
        return "ไม่มีรูป"
    
    @property
    def og_image_size(self):
        """Get OG image dimensions if available"""
        if self.og_image:
            try:
                from PIL import Image
                with self.og_image.open() as img:
                    pil_img = Image.open(img)
                    return f"{pil_img.width}x{pil_img.height}"
            except:
                return "ไม่สามารถอ่านขนาดได้"
        return "ไม่มีรูป"
    
    @property
    def seo_title_display(self):
        """Get SEO title or fallback to name"""
        return self.seo_title if self.seo_title else self.name
    
    @property
    def og_title_display(self):
        """Get OG title or fallback to SEO title or name"""
        return self.og_title if self.og_title else (self.seo_title if self.seo_title else self.name)