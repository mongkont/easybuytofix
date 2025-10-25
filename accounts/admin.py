from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import UserProfile
import pytz
from datetime import datetime


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    fk_name = 'user'  # Specify which ForeignKey to use
    can_delete = False
    verbose_name_plural = 'โปรไฟล์'
    readonly_fields = ('created_at_thai', 'updated_at_thai', 'created_by_display', 'updated_by_display', 'avatar_preview')
    
    fieldsets = (
        ('ข้อมูลผู้ใช้', {
            'fields': ('avatar_preview', 'avatar')
        }),
        ('ข้อมูลติดต่อ', {
            'fields': ('phone_number', 'address')
        }),
        ('ข้อมูลส่วนตัว', {
            'fields': ('bio', 'date_of_birth')
        }),
        ('ข้อมูลระบบ', {
            'fields': ('created_at_thai', 'created_by_display', 'updated_at_thai', 'updated_by_display'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make created_by and updated_by readonly"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.extend(['created_by'])
        return readonly
    
    def avatar_preview(self, obj):
        """Display avatar preview"""
        if obj and obj.avatar:
            return mark_safe(
                f'<div class="avatar-preview"><img src="{obj.avatar.url}" alt="Avatar" /></div>'
            )
        return "ไม่มีรูป"
    avatar_preview.short_description = 'รูปโปรไฟล์'
    avatar_preview.allow_tags = True
    
    def created_at_thai(self, obj):
        """Display creation date in Thai Buddhist Era"""
        if obj and obj.created_at:
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
        if obj and obj.updated_at:
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
    
    def created_by_display(self, obj):
        """Display creator name"""
        if obj and obj.created_by:
            full_name = obj.created_by.get_full_name()
            if full_name:
                return f"{full_name} ({obj.created_by.username})"
            return obj.created_by.username
        return "-"
    created_by_display.short_description = 'ผู้สร้าง'
    
    def updated_by_display(self, obj):
        """Display updater name"""
        if obj and obj.updated_by:
            full_name = obj.updated_by.get_full_name()
            if full_name:
                return f"{full_name} ({obj.updated_by.username})"
            return obj.updated_by.username
        return "-"
    updated_by_display.short_description = 'ผู้แก้ไข'


class UserAdmin(BaseUserAdmin):
    """Custom User Admin with Profile inline"""
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        """Show inline only when editing user"""
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model"""
    
    list_display = ('user', 'full_name', 'phone_number', 'avatar_preview', 'created_by_display', 'updated_by_display', 'created_at_thai')
    list_filter = ('created_at', 'updated_at', 'user__is_active', 'user__is_staff')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')
    readonly_fields = ('created_at_thai', 'updated_at_thai', 'created_by_display', 'updated_by_display', 'avatar_preview')
    
    class Media:
        css = {
            'all': ('css/admin.css',)
        }
    
    fieldsets = (
        ('ข้อมูลผู้ใช้', {
            'fields': ('user', 'avatar_preview')
        }),
        ('จัดการรูปโปรไฟล์', {
            'fields': ('avatar',),
            'classes': ('collapse',),
            'description': 'ใช้ส่วนนี้เพื่อเปลี่ยนรูปโปรไฟล์'
        }),
        ('ข้อมูลติดต่อ', {
            'fields': ('phone_number', 'address')
        }),
        ('ข้อมูลส่วนตัว', {
            'fields': ('bio', 'date_of_birth')
        }),
        ('ข้อมูลระบบ', {
            'fields': ('created_at_thai', 'created_by_display', 'updated_at_thai', 'updated_by_display'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        """Display user's full name"""
        return obj.full_name
    full_name.short_description = 'ชื่อ-นามสกุล'
    
    def avatar_preview(self, obj):
        """Display avatar preview"""
        if obj.avatar:
            return mark_safe(
                f'<div class="avatar-preview"><img src="{obj.avatar.url}" alt="Avatar" /></div>'
            )
        return "ไม่มีรูป"
    avatar_preview.short_description = 'รูปโปรไฟล์'
    avatar_preview.allow_tags = True
    
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
            import pytz
            from datetime import datetime
            
            # Convert to Thai timezone
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
            import pytz
            from datetime import datetime
            
            # Convert to Thai timezone
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
    
    def get_readonly_fields(self, request, obj=None):
        """Make created_by readonly for existing objects"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.append('created_by')
        return readonly


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'get_full_name', 'email', 'get_phone_number', 'get_avatar_preview', 'is_active', 'is_staff', 'date_joined_thai')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    class Media:
        css = {
            'all': ('css/admin.css',)
        }
    
    def get_full_name(self, obj):
        """Display user's full name"""
        full_name = obj.get_full_name()
        return full_name if full_name else obj.username
    get_full_name.short_description = 'ชื่อ-นามสกุล'
    
    def get_phone_number(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else ''
    get_phone_number.short_description = 'เบอร์โทรศัพท์'
    
    def get_avatar_preview(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return format_html(
                '<div class="avatar-preview"><img src="{}" /></div>',
                obj.profile.avatar.url
            )
        return "ไม่มีรูป"
    get_avatar_preview.short_description = 'รูปโปรไฟล์'
    
    def date_joined_thai(self, obj):
        """Display date joined in Thai Buddhist Era"""
        if obj.date_joined:
            # Convert to Thai timezone and Buddhist Era
            thai_tz = pytz.timezone('Asia/Bangkok')
            thai_time = obj.date_joined.astimezone(thai_tz)
            
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
    date_joined_thai.short_description = 'วันที่สมัคร'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)