from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import os
from datetime import datetime
from django.utils.text import slugify
import re
from unidecode import unidecode

User = get_user_model()


def category_image_upload_path(instance, filename):
    """Generate upload path for category images"""
    ext = filename.split('.')[-1]
    filename = f"category_{instance.pk}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('categories', filename)


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


def thai_slugify(text):
    """Convert Thai text to URL-friendly slug"""
    if not text:
        return ''
    
    # Thai character mapping
    thai_map = {
        'ก': 'k', 'ข': 'kh', 'ฃ': 'kh', 'ค': 'kh', 'ฅ': 'kh', 'ฆ': 'kh',
        'ง': 'ng', 'จ': 'ch', 'ฉ': 'ch', 'ช': 'ch', 'ซ': 's', 'ฌ': 'ch',
        'ญ': 'y', 'ด': 'd', 'ต': 't', 'ถ': 'th', 'ท': 'th', 'ธ': 'th',
        'น': 'n', 'บ': 'b', 'ป': 'p', 'ผ': 'ph', 'ฝ': 'f', 'พ': 'ph',
        'ฟ': 'f', 'ภ': 'ph', 'ม': 'm', 'ย': 'y', 'ร': 'r', 'ล': 'l',
        'ว': 'w', 'ศ': 's', 'ษ': 's', 'ส': 's', 'ห': 'h', 'ฬ': 'l',
        'อ': '', 'ฮ': 'h',
        'ะ': 'a', 'ั': 'a', 'า': 'a', 'ำ': 'am', 'ิ': 'i', 'ี': 'i',
        'ึ': 'ue', 'ื': 'ue', 'ุ': 'u', 'ู': 'u', 'เ': 'e', 'แ': 'ae',
        'โ': 'o', 'ใ': 'ai', 'ไ': 'ai', '็': '', '่': '', '้': '',
        '๊': '', '๋': '', '์': '', 'ํ': '', '๎': '', '๏': '', '๐': '0',
        '๑': '1', '๒': '2', '๓': '3', '๔': '4', '๕': '5',
        '๖': '6', '๗': '7', '๘': '8', '๙': '9'
    }
    
    # Convert Thai characters
    result = ''
    for char in text:
        if char in thai_map:
            result += thai_map[char]
        elif char.isalnum():
            result += char
        elif char in ' -_':
            result += '-'
        else:
            result += ''
    
    # Clean up the result
    result = re.sub(r'-+', '-', result)  # Replace multiple dashes with single dash
    result = result.strip('-')  # Remove leading/trailing dashes
    
    return result.lower()


class Category(models.Model):
    """Product category model"""
    name = models.CharField(
        _("ชื่อหมวดหมู่"),
        max_length=100,
        unique=True,
        help_text=_("ชื่อหมวดหมู่สินค้า")
    )
    slug = models.CharField(
        _("Slug"),
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("URL-friendly version of the name (auto-generated or manual)")
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

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = custom_slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

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