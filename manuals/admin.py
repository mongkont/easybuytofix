from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_summernote.admin import SummernoteModelAdmin
from .models import ManualCategory, Manual, ManualAttachment
import pytz
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()


@admin.register(ManualCategory)
class ManualCategoryAdmin(admin.ModelAdmin):
    """Admin for ManualCategory model"""
    
    list_display = ('name', 'slug', 'description_preview', 'icon', 'order', 'is_active', 'created_by_display', 'updated_by_display', 'created_at_thai')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'slug', 'description')
    readonly_fields = ('created_at_thai', 'updated_at_thai', 'created_by_display', 'updated_by_display')
    ordering = ('order', 'name')
    prepopulated_fields = {'slug': ('name',)}
    
    class Media:
        css = {
            'all': ('css/admin.css',)
        }
    
    fieldsets = (
        ('ข้อมูลหมวดหมู่', {
            'fields': ('name', 'slug', 'description', 'icon', 'order', 'is_active')
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
            thai_tz = pytz.timezone('Asia/Bangkok')
            thai_time = obj.created_at.astimezone(thai_tz)
            buddhist_year = thai_time.year + 543
            thai_months = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
            month_name = thai_months[thai_time.month - 1]
            formatted_date = f"{thai_time.day} {month_name} {buddhist_year}, {thai_time.strftime('%H:%M')}"
            return formatted_date
        return "-"
    created_at_thai.short_description = 'วันที่สร้าง'

    def updated_at_thai(self, obj):
        """Display update date in Thai Buddhist Era"""
        if obj.updated_at:
            thai_tz = pytz.timezone('Asia/Bangkok')
            thai_time = obj.updated_at.astimezone(thai_tz)
            buddhist_year = thai_time.year + 543
            thai_months = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
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
    
    def get_readonly_fields(self, request, obj=None):
        """Make created_by readonly for existing objects"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.append('created_by')
        return readonly


@admin.register(Manual)
class ManualAdmin(SummernoteModelAdmin):
    """Admin for Manual model"""
    
    summernote_fields = ('content',)
    
    list_display = ('title', 'category', 'order_display', 'is_public', 'visible_groups_display', 'is_active', 'created_by_display', 'updated_by_display', 'created_at_thai')
    list_filter = ('category', 'is_public', 'is_active', 'visible_to_groups', 'created_at', 'updated_at')
    search_fields = ('title', 'slug', 'content', 'seo_title', 'seo_description')
    readonly_fields = ('created_at_thai', 'updated_at_thai', 'created_by_display', 'updated_by_display')
    ordering = ('category__order', 'category__name', 'title')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('visible_to_groups',)
    
    class Media:
        css = {
            'all': ('css/admin.css',)
        }
    
    fieldsets = (
        ('ข้อมูลคู่มือ', {
            'fields': ('title', 'slug', 'category', 'content')
        }),
        ('การแสดงผล', {
            'fields': ('is_public', 'visible_to_groups', 'order_before'),
            'description': 'กำหนดว่าใครสามารถเห็นคู่มือนี้ได้ และลำดับการแสดงผล'
        }),
        ('SEO Optimization', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',),
            'description': 'ข้อมูลสำหรับ SEO (Search Engine Optimization)'
        }),
        ('ข้อมูลการจัดการ', {
            'fields': ('is_active', 'created_at_thai', 'created_by_display', 'updated_at_thai', 'updated_by_display'),
            'classes': ('collapse',)
        }),
    )
    
    def order_display(self, obj):
        """Display order information"""
        if obj.order_before:
            return f"อยู่ก่อน: {obj.order_before.title}"
        return "อยู่ท้ายสุด"
    order_display.short_description = 'ลำดับ'
    
    def visible_groups_display(self, obj):
        """Display visible groups"""
        if obj.is_public:
            return "สาธารณะ"
        groups = obj.visible_to_groups.all()
        if groups:
            return ", ".join([group.name for group in groups])
        return "ไม่มี"
    visible_groups_display.short_description = 'แสดงสำหรับ'
    
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
            thai_tz = pytz.timezone('Asia/Bangkok')
            thai_time = obj.created_at.astimezone(thai_tz)
            buddhist_year = thai_time.year + 543
            thai_months = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
            month_name = thai_months[thai_time.month - 1]
            formatted_date = f"{thai_time.day} {month_name} {buddhist_year}, {thai_time.strftime('%H:%M')}"
            return formatted_date
        return "-"
    created_at_thai.short_description = 'วันที่สร้าง'

    def updated_at_thai(self, obj):
        """Display update date in Thai Buddhist Era"""
        if obj.updated_at:
            thai_tz = pytz.timezone('Asia/Bangkok')
            thai_time = obj.updated_at.astimezone(thai_tz)
            buddhist_year = thai_time.year + 543
            thai_months = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
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
    
    def get_readonly_fields(self, request, obj=None):
        """Make created_by readonly for existing objects"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.append('created_by')
        return readonly
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize order_before dropdown"""
        if db_field.name == "order_before":
            # Get current manual if editing
            if hasattr(request, 'resolver_match') and request.resolver_match.kwargs.get('object_id'):
                current_manual_id = request.resolver_match.kwargs['object_id']
                kwargs["queryset"] = Manual.objects.exclude(pk=current_manual_id).filter(is_active=True)
            else:
                kwargs["queryset"] = Manual.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)