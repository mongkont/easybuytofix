from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os

User = get_user_model()

class BackupHistory(models.Model):
    """Backup History Model"""
    
    ENVIRONMENT_CHOICES = [
        ('local', _('Local')),
        ('production', _('Production')),
    ]
    
    BACKUP_TYPE_CHOICES = [
        ('manual', _('Manual')),
        ('scheduled', _('Scheduled')),
    ]
    
    STATUS_CHOICES = [
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]
    
    filename = models.CharField(
        _("ชื่อไฟล์"),
        max_length=255,
        help_text=_("ชื่อไฟล์ backup พร้อม version และ timestamp")
    )
    environment = models.CharField(
        _("Environment"),
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        help_text=_("Local หรือ Production")
    )
    file_size = models.BigIntegerField(
        _("ขนาดไฟล์"),
        default=0,
        help_text=_("ขนาดไฟล์เป็น bytes")
    )
    postgresql_version = models.CharField(
        _("PostgreSQL Version"),
        max_length=20,
        blank=True,
        null=True,
        help_text=_("เวอร์ชัน PostgreSQL")
    )
    backup_type = models.CharField(
        _("ประเภท Backup"),
        max_length=20,
        choices=BACKUP_TYPE_CHOICES,
        default='manual',
        help_text=_("Manual หรือ Scheduled")
    )
    status = models.CharField(
        _("สถานะ"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        help_text=_("สถานะการ backup")
    )
    progress = models.PositiveIntegerField(
        _("ความคืบหน้า"),
        default=0,
        help_text=_("เปอร์เซ็นต์ความคืบหน้า (0-100)")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_backups',
        blank=True,
        null=True,
        verbose_name=_("ผู้สร้าง")
    )
    created_at = models.DateTimeField(
        _("วันที่สร้าง"),
        auto_now_add=True
    )
    notes = models.TextField(
        _("หมายเหตุ"),
        blank=True,
        null=True,
        help_text=_("หมายเหตุเพิ่มเติม")
    )
    
    class Meta:
        verbose_name = _("ประวัติการ Backup")
        verbose_name_plural = _("ประวัติการ Backup")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.filename} ({self.environment})"
    
    @property
    def file_size_display(self):
        """แสดงขนาดไฟล์แบบ human readable"""
        if self.file_size == 0:
            return "0 B"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    @property
    def file_path(self):
        """Path ของไฟล์ backup"""
        if self.environment == 'local':
            return os.path.join(settings.BACKUP_LOCAL_DIR, self.filename)
        else:
            return os.path.join(settings.BACKUP_PRODUCTION_DIR, self.filename)
    
    @property
    def file_exists(self):
        """ตรวจสอบว่าไฟล์มีอยู่จริงหรือไม่"""
        return os.path.exists(self.file_path)


class BackupSchedule(models.Model):
    """Backup Schedule Model"""
    
    ENVIRONMENT_CHOICES = [
        ('local', _('Local')),
        ('production', _('Production')),
    ]
    
    SCHEDULE_TYPE_CHOICES = [
        ('daily', _('ทุกวัน')),
        ('weekly', _('ทุกสัปดาห์')),
        ('monthly', _('ทุกเดือน')),
    ]
    
    name = models.CharField(
        _("ชื่อ Schedule"),
        max_length=100,
        help_text=_("ชื่อสำหรับ schedule นี้")
    )
    environment = models.CharField(
        _("Environment"),
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        help_text=_("Local หรือ Production")
    )
    schedule_type = models.CharField(
        _("ประเภท Schedule"),
        max_length=20,
        choices=SCHEDULE_TYPE_CHOICES,
        default='daily',
        help_text=_("ความถี่ในการ backup")
    )
    time = models.TimeField(
        _("เวลา"),
        help_text=_("เวลาที่ต้องการ backup (เวลาไทย)")
    )
    is_active = models.BooleanField(
        _("เปิดใช้งาน"),
        default=True,
        help_text=_("เปิด/ปิดใช้งาน schedule นี้")
    )
    last_run = models.DateTimeField(
        _("รันครั้งล่าสุด"),
        blank=True,
        null=True,
        help_text=_("วันเวลาที่ backup ครั้งล่าสุด")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_schedules',
        blank=True,
        null=True,
        verbose_name=_("ผู้สร้าง")
    )
    created_at = models.DateTimeField(
        _("วันที่สร้าง"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("วันที่แก้ไข"),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _("ตารางการ Backup")
        verbose_name_plural = _("ตารางการ Backup")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.environment}) - {self.schedule_type}"
    
    @property
    def next_run_display(self):
        """แสดงเวลาที่จะรันครั้งถัดไป"""
        if not self.is_active:
            return "ปิดใช้งาน"
        
        from datetime import datetime, timedelta
        import pytz
        
        thai_tz = pytz.timezone('Asia/Bangkok')
        now = datetime.now(thai_tz)
        
        # Convert time to time object if it's a string
        if isinstance(self.time, str):
            from datetime import time
            time_obj = time.fromisoformat(self.time)
        else:
            time_obj = self.time
        
        if self.schedule_type == 'daily':
            next_run = now.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif self.schedule_type == 'weekly':
            # รันทุกวันอาทิตย์
            days_ahead = 6 - now.weekday()  # 6 = Sunday
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)
        else:  # monthly
            # รันวันที่ 1 ของเดือนถัดไป
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)
            next_run = next_month.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)
        
        return next_run.strftime('%d/%m/%Y %H:%M')