from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
import pytz
from datetime import datetime
from .models import BackupHistory, BackupSchedule
from .views import backup_view, restore_view, progress_api, download_backup, delete_backup
from .utils import thai_datetime, get_postgresql_version

User = get_user_model()


@admin.register(BackupHistory)
class BackupHistoryAdmin(admin.ModelAdmin):
    """Admin for BackupHistory model"""
    
    list_display = (
        'filename', 
        'environment', 
        'file_size_display', 
        'postgresql_version',
        'backup_type',
        'status',
        'progress_display',
        'download_button',
        'restore_button',
        'created_by_display',
        'created_at_thai'
    )
    list_filter = ('environment', 'backup_type', 'status', 'created_at')
    search_fields = ('filename', 'notes')
    readonly_fields = (
        'created_at_thai', 
        'created_by_display', 
        'file_size_display',
        'file_exists_display',
        'progress_display'
    )
    ordering = ['-created_at']
    
    class Media:
        css = {
            'all': ('css/admin.css',)
        }
    
    fieldsets = (
        ('ข้อมูล Backup', {
            'fields': ('filename', 'environment', 'backup_type', 'status', 'progress_display')
        }),
        ('รายละเอียดไฟล์', {
            'fields': ('file_size_display', 'postgresql_version', 'file_exists_display'),
            'classes': ('collapse',)
        }),
        ('ข้อมูลการจัดการ', {
            'fields': ('created_at_thai', 'created_by_display', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['backup_now_local', 'backup_now_production', 'download_selected_backups', 'delete_selected_backups', 'restore_selected_backups']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('backup/', backup_view, name='backup_database'),
            path('restore/', restore_view, name='restore_database'),
            path('progress/<int:backup_id>/', progress_api, name='backup_progress'),
            path('<int:backup_id>/download/', download_backup, name='download_backup'),
            path('<int:backup_id>/delete/', delete_backup, name='delete_backup'),
        ]
        return custom_urls + urls
    
    def file_size_display(self, obj):
        """แสดงขนาดไฟล์แบบ human readable"""
        return obj.file_size_display
    file_size_display.short_description = 'ขนาดไฟล์'
    
    def progress_display(self, obj):
        """แสดง progress bar"""
        if obj.status == 'in_progress':
            return format_html(
                '<div class="progress-bar" style="width: 200px; background-color: #f0f0f0; border-radius: 3px;">'
                '<div style="width: {}%; background-color: #4CAF50; height: 20px; border-radius: 3px; text-align: center; color: white; line-height: 20px;">{}%</div>'
                '</div>',
                obj.progress,
                obj.progress
            )
        elif obj.status == 'completed':
            return format_html('<span style="color: green;">✓ เสร็จสิ้น</span>')
        elif obj.status == 'failed':
            return format_html('<span style="color: red;">✗ ล้มเหลว</span>')
        return '-'
    progress_display.short_description = 'ความคืบหน้า'
    
    def created_by_display(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            if full_name:
                return f"{full_name} ({obj.created_by.username})"
            return obj.created_by.username
        return "ระบบ"
    created_by_display.short_description = 'ผู้สร้าง'
    
    def created_at_thai(self, obj):
        return thai_datetime(obj.created_at)
    created_at_thai.short_description = 'วันที่สร้าง'
    
    def file_exists_display(self, obj):
        if obj.file_exists:
            return format_html('<span style="color: green;">✓ มีไฟล์</span>')
        else:
            return format_html('<span style="color: red;">✗ ไม่มีไฟล์</span>')
    file_exists_display.short_description = 'สถานะไฟล์'
    
    def download_button(self, obj):
        """ปุ่มดาวน์โหลด"""
        if obj.file_exists and obj.status == 'completed':
            return format_html(
                '<a href="/admin/dbbackup/backuphistory/{}/download/" class="button" style="background-color: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; font-size: 12px;">ดาวน์โหลด</a>',
                obj.id
            )
        else:
            return format_html('<span style="color: #ccc;">-</span>')
    download_button.short_description = 'ดาวน์โหลด'
    
    def restore_button(self, obj):
        """ปุ่ม Restore"""
        if obj.file_exists and obj.status == 'completed':
            return format_html(
                '<a href="/admin/dbbackup/backuphistory/restore/?backup_file={}" class="button" style="background-color: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; font-size: 12px;">Restore</a>',
                obj.file_path
            )
        else:
            return format_html('<span style="color: #ccc;">-</span>')
    restore_button.short_description = 'Restore'
    
    def backup_now_local(self, request, queryset):
        """Backup local ทันที"""
        try:
            from .utils import run_pg_dump
            from datetime import datetime
            
            pg_version = get_postgresql_version()
            timestamp = datetime.now().strftime('%y%m%d_%H%M')
            filename = f'bk_{timestamp}_pg{pg_version}_loc.sql'
            
            backup_history = BackupHistory.objects.create(
                filename=filename,
                environment='local',
                postgresql_version=pg_version,
                backup_type='manual',
                status='in_progress',
                progress=0,
                created_by=request.user,
                notes='Manual backup from admin action'
            )
            
            def progress_callback(progress):
                backup_history.progress = progress
                backup_history.save()
            
            success = run_pg_dump(backup_history, progress_callback)
            
            if success:
                messages.success(request, f'Backup local สำเร็จ: {filename}')
            else:
                messages.error(request, f'Backup local ล้มเหลว: {backup_history.notes}')
                
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {e}')
    
    backup_now_local.short_description = "Backup Local ทันที"
    
    def backup_now_production(self, request, queryset):
        """Backup production ทันที"""
        try:
            from .utils import run_pg_dump
            from datetime import datetime
            
            pg_version = get_postgresql_version()
            timestamp = datetime.now().strftime('%y%m%d_%H%M')
            filename = f'bk_{timestamp}_pg{pg_version}_pro.sql'
            
            backup_history = BackupHistory.objects.create(
                filename=filename,
                environment='production',
                postgresql_version=pg_version,
                backup_type='manual',
                status='in_progress',
                progress=0,
                created_by=request.user,
                notes='Manual backup from admin action'
            )
            
            def progress_callback(progress):
                backup_history.progress = progress
                backup_history.save()
            
            success = run_pg_dump(backup_history, progress_callback)
            
            if success:
                messages.success(request, f'Backup production สำเร็จ: {filename}')
            else:
                messages.error(request, f'Backup production ล้มเหลว: {backup_history.notes}')
                
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {e}')
    
    backup_now_production.short_description = "Backup Production ทันที"
    
    def download_selected_backups(self, request, queryset):
        """ดาวน์โหลด backup ที่เลือก"""
        if queryset.count() == 1:
            backup = queryset.first()
            if backup.file_exists:
                return redirect(f'/admin/dbbackup/backuphistory/{backup.id}/download/')
            else:
                messages.error(request, 'ไม่พบไฟล์ backup')
        else:
            messages.error(request, 'กรุณาเลือก backup เพียง 1 ไฟล์')
    
    download_selected_backups.short_description = "ดาวน์โหลด Backup"
    
    def delete_selected_backups(self, request, queryset):
        """ลบ backup ที่เลือก"""
        count = 0
        for backup in queryset:
            try:
                if backup.file_exists:
                    import os
                    os.remove(backup.file_path)
                backup.delete()
                count += 1
            except Exception as e:
                messages.error(request, f'ไม่สามารถลบ {backup.filename}: {e}')
        
        if count > 0:
            messages.success(request, f'ลบ backup เรียบร้อยแล้ว {count} ไฟล์')
    
    delete_selected_backups.short_description = "ลบ Backup"
    
    def restore_selected_backups(self, request, queryset):
        """Restore backup ที่เลือก"""
        if queryset.count() == 1:
            backup = queryset.first()
            if backup.file_exists and backup.status == 'completed':
                # Redirect ไปหน้า restore form
                return HttpResponseRedirect(f'/admin/dbbackup/backuphistory/restore/?backup_file={backup.file_path}')
            else:
                messages.error(request, 'ไม่สามารถ restore ไฟล์นี้ได้')
        else:
            messages.error(request, 'กรุณาเลือก backup เพียง 1 ไฟล์')
    
    restore_selected_backups.short_description = "Restore Backup"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['backup_url'] = '/admin/dbbackup/backuphistory/backup/'
        extra_context['restore_url'] = '/admin/dbbackup/backuphistory/restore/'
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(BackupSchedule)
class BackupScheduleAdmin(admin.ModelAdmin):
    """Admin for BackupSchedule model"""
    
    list_display = (
        'name', 
        'environment', 
        'schedule_type', 
        'time', 
        'is_active',
        'last_run_thai',
        'next_run_display'
    )
    list_filter = ('environment', 'schedule_type', 'is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at_thai', 'created_by_display', 'last_run_thai', 'next_run_display')
    ordering = ['name']
    
    class Media:
        css = {
            'all': ('css/admin.css',)
        }
    
    fieldsets = (
        ('ข้อมูล Schedule', {
            'fields': ('name', 'environment', 'schedule_type', 'time', 'is_active')
        }),
        ('ข้อมูลการจัดการ', {
            'fields': ('next_run_display', 'created_at_thai', 'created_by_display'),
            'classes': ('collapse',)
        }),
    )
    
    def created_by_display(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            if full_name:
                return f"{full_name} ({obj.created_by.username})"
            return obj.created_by.username
        return "-"
    created_by_display.short_description = 'ผู้สร้าง'
    
    def created_at_thai(self, obj):
        return thai_datetime(obj.created_at)
    created_at_thai.short_description = 'วันที่สร้าง'
    
    def last_run_thai(self, obj):
        return thai_datetime(obj.last_run)
    last_run_thai.short_description = 'รันครั้งล่าสุด'
    
    def next_run_display(self, obj):
        return obj.next_run_display
    next_run_display.short_description = 'รันครั้งถัดไป'
    
    def save_model(self, request, obj, form, change):
        """Set created_by"""
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        """Make created_by readonly for existing objects"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.append('created_by')
        return readonly