from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Category
import pytz
from datetime import datetime
from django.contrib.auth import get_user_model
from django.urls import path
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.files.storage import default_storage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model"""
    
    list_display = ('name', 'slug', 'description_preview', 'image_preview', 'image_size_display', 'seo_title_display', 'is_active', 'created_by_display', 'updated_by_display', 'created_at_thai')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'slug', 'description', 'seo_title', 'seo_description')
    readonly_fields = ('created_at_thai', 'updated_at_thai', 'created_by_display', 'updated_by_display', 'image_preview', 'image_size_display', 'og_image_preview', 'og_image_size_display', 'image_with_delete_button', 'og_image_with_delete_button')
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    actions = ['delete_category_images']
    
    class Media:
        css = {
            'all': ('css/admin.css',)
        }
    
    fieldsets = (
        ('ข้อมูลหมวดหมู่', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('รูปหมวดหมู่', {
            'fields': ('image_with_delete_button', 'image', 'image_size_display', 'alt_text')
        }),
        ('SEO Optimization', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',),
            'description': 'ข้อมูลสำหรับ SEO (Search Engine Optimization)'
        }),
        ('Open Graph (Social Media)', {
            'fields': ('og_image_with_delete_button', 'og_image', 'og_image_size_display', 'og_title', 'og_description'),
            'classes': ('collapse',),
            'description': 'ข้อมูลสำหรับแชร์ใน Social Media'
        }),
        ('ข้อมูลการจัดการ', {
            'fields': ('created_at_thai', 'created_by_display', 'updated_at_thai', 'updated_by_display'),
            'classes': ('collapse',)
        }),
    )
    
    def description_preview(self, obj):
        """Display description preview"""
        if obj.description:
            return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
        return "-"
    description_preview.short_description = 'รายละเอียด'
    
    def image_preview(self, obj):
        """Display image preview"""
        if obj.image:
            return mark_safe(
                f'<div class="category-image-preview"><img src="{obj.image.url}" alt="Category Image" /></div>'
            )
        return "ไม่มีรูป"
    image_preview.short_description = 'รูปหมวดหมู่'
    image_preview.allow_tags = True
    
    def image_size_display(self, obj):
        """Display image size"""
        return obj.image_size
    image_size_display.short_description = 'ขนาดรูป'
    
    def seo_title_display(self, obj):
        """Display SEO title"""
        return obj.seo_title_display
    seo_title_display.short_description = 'SEO Title'
    
    def og_image_preview(self, obj):
        """Display OG image preview"""
        if obj.og_image:
            return mark_safe(
                f'<div class="og-image-preview"><img src="{obj.og_image.url}" alt="OG Image" /></div>'
            )
        return "ไม่มีรูป"
    og_image_preview.short_description = 'OG Image Preview'
    og_image_preview.allow_tags = True
    
    def og_image_size_display(self, obj):
        """Display OG image size"""
        return obj.og_image_size
    og_image_size_display.short_description = 'ขนาด OG Image'
    
    def slug_display(self, obj):
        """Display slug with auto-generation info"""
        if obj.slug:
            return f"{obj.slug} (auto-generated)"
        return "จะสร้างอัตโนมัติเมื่อบันทึก"
    slug_display.short_description = 'Slug'
    
    def image_with_delete_button(self, obj):
        """Display image preview with delete button for detail view"""
        if obj.image:
            delete_url = f'/admin/products/category/{obj.pk}/delete-image/'
            return mark_safe(
                f'''
                <div class="category-image-preview">
                    <img src="{obj.image.url}" alt="Category Image" />
                    <br>
                    <a href="{delete_url}" class="button" style="margin-top: 10px; background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;" 
                       onclick="return confirm('คุณแน่ใจหรือไม่ที่จะลบรูปหมวดหมู่นี้?')">
                        ลบรูป
                    </a>
                </div>
                '''
            )
        return "ไม่มีรูป"
    image_with_delete_button.short_description = 'รูปหมวดหมู่'
    image_with_delete_button.allow_tags = True
    
    def og_image_with_delete_button(self, obj):
        """Display OG image preview with delete button for detail view"""
        if obj.og_image:
            delete_url = f'/admin/products/category/{obj.pk}/delete-og-image/'
            return mark_safe(
                f'''
                <div class="og-image-preview">
                    <img src="{obj.og_image.url}" alt="OG Image" />
                    <br>
                    <a href="{delete_url}" class="button" style="margin-top: 10px; background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;" 
                       onclick="return confirm('คุณแน่ใจหรือไม่ที่จะลบรูป OG นี้?')">
                        ลบรูป OG
                    </a>
                </div>
                '''
            )
        return "ไม่มีรูป"
    og_image_with_delete_button.short_description = 'รูป OG'
    og_image_with_delete_button.allow_tags = True
    
    def created_by_display(self, obj):
        """Display creator name"""
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            if full_name:
                return f"{full_name} ({obj.created_by.username})"
            return obj.created_by.username
        return "-"
    created_by_display.short_description = 'ผู้สร้าง'
    
    def updated_by_display(self, obj):
        """Display updater name"""
        if obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            if full_name:
                return f"{full_name} ({obj.updated_by.username})"
            return obj.updated_by.username
        return "-"
    updated_by_display.short_description = 'ผู้แก้ไข'
    
    def created_at_thai(self, obj):
        """Display creation date in Thai Buddhist Era"""
        if obj.created_at:
            # Convert to Thai timezone and Buddhist Era
            thai_tz = pytz.timezone('Asia/Bangkok')
            thai_time = obj.created_at.astimezone(thai_tz)
            
            # Convert to Buddhist Era (add 543 years)
            buddhist_year = thai_time.year + 543
            
            # Format in Thai
            thai_months = [
                'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
                'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
            ]
            
            month_name = thai_months[thai_time.month - 1]
            formatted_date = f"{thai_time.day} {month_name} {buddhist_year}, {thai_time.strftime('%H:%M')}"
            
            return formatted_date
        return "-"
    created_at_thai.short_description = 'วันที่สร้าง'
    
    def updated_at_thai(self, obj):
        """Display update date in Thai Buddhist Era"""
        if obj.updated_at:
            # Convert to Thai timezone and Buddhist Era
            thai_tz = pytz.timezone('Asia/Bangkok')
            thai_time = obj.updated_at.astimezone(thai_tz)
            
            # Convert to Buddhist Era (add 543 years)
            buddhist_year = thai_time.year + 543
            
            # Format in Thai
            thai_months = [
                'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
                'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
            ]
            
            month_name = thai_months[thai_time.month - 1]
            formatted_date = f"{thai_time.day} {month_name} {buddhist_year}, {thai_time.strftime('%H:%M')}"
            
            return formatted_date
        return "-"
    updated_at_thai.short_description = 'วันที่แก้ไข'
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by"""
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def delete_category_images(self, request, queryset):
        """Delete images for selected categories"""
        from django.contrib import messages
        from django.core.files.storage import default_storage
        
        deleted_count = 0
        for category in queryset:
            try:
                # Delete main image
                if category.image:
                    if default_storage.exists(category.image.name):
                        default_storage.delete(category.image.name)
                    category.image = None
                
                # Delete OG image
                if category.og_image:
                    if default_storage.exists(category.og_image.name):
                        default_storage.delete(category.og_image.name)
                    category.og_image = None
                
                category.save()
                deleted_count += 1
            except Exception as e:
                messages.error(request, f"Error deleting images for {category.name}: {e}")
        
        if deleted_count > 0:
            messages.success(request, f"ลบรูปหมวดหมู่ {deleted_count} รายการเรียบร้อยแล้ว")
        else:
            messages.warning(request, "ไม่มีรูปหมวดหมู่ที่สามารถลบได้")
    
    delete_category_images.short_description = "ลบรูปหมวดหมู่"
    
    def get_urls(self):
        """Add custom URLs for image management"""
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/delete-image/', self.delete_image_view, name='products_category_delete_image'),
            path('<int:object_id>/delete-og-image/', self.delete_og_image_view, name='products_category_delete_og_image'),
        ]
        return custom_urls + urls
    
    def delete_image_view(self, request, object_id):
        """Delete main image for specific category"""
        category = get_object_or_404(Category, pk=object_id)
        
        if category.image:
            try:
                if default_storage.exists(category.image.name):
                    default_storage.delete(category.image.name)
                
                category.image = None
                category.save()
                messages.success(request, f"ลบรูปหมวดหมู่ {category.name} เรียบร้อยแล้ว")
            except Exception as e:
                messages.error(request, f"Error deleting image: {e}")
        else:
            messages.warning(request, "ไม่มีรูปหมวดหมู่ที่สามารถลบได้")
        
        return redirect(f'/admin/products/category/{object_id}/change/')
    
    def delete_og_image_view(self, request, object_id):
        """Delete OG image for specific category"""
        category = get_object_or_404(Category, pk=object_id)
        
        if category.og_image:
            try:
                if default_storage.exists(category.og_image.name):
                    default_storage.delete(category.og_image.name)
                
                category.og_image = None
                category.save()
                messages.success(request, f"ลบรูป OG ของหมวดหมู่ {category.name} เรียบร้อยแล้ว")
            except Exception as e:
                messages.error(request, f"Error deleting OG image: {e}")
        else:
            messages.warning(request, "ไม่มีรูป OG ที่สามารถลบได้")
        
        return redirect(f'/admin/products/category/{object_id}/change/')
    
    def get_readonly_fields(self, request, obj=None):
        """Make created_by readonly for existing objects"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.append('created_by')
        return readonly