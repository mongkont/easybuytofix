from django.utils import timezone
from django.contrib.auth import get_user_model
from dbbackup.models import BackupSchedule, BackupHistory
from dbbackup.utils import get_postgresql_version, run_pg_dump
import pytz
from datetime import datetime, timedelta

User = get_user_model()


def run_scheduled_backups():
    """ฟังก์ชันสำหรับรัน scheduled backup (ใช้กับ django-crontab)"""
    thai_tz = pytz.timezone('Asia/Bangkok')
    now = timezone.now().astimezone(thai_tz)
    
    # ดึง schedules ที่ active
    active_schedules = BackupSchedule.objects.filter(is_active=True)
    
    for schedule in active_schedules:
        if should_run_backup(schedule, now):
            run_scheduled_backup(schedule, now)


def should_run_backup(schedule, now):
    """ตรวจสอบว่าควรรัน backup หรือไม่"""
    # เช็คว่าเคยรันแล้วหรือยังวันนี้
    if schedule.last_run:
        last_run_thai = schedule.last_run.astimezone(pytz.timezone('Asia/Bangkok'))
        
        if schedule.schedule_type == 'daily':
            # รันทุกวันในเวลาที่กำหนด
            if last_run_thai.date() == now.date():
                return False  # รันแล้ววันนี้
            
            # เช็คว่าเวลาผ่านไปแล้วหรือยัง
            scheduled_time = now.replace(
                hour=schedule.time.hour,
                minute=schedule.time.minute,
                second=0,
                microsecond=0
            )
            return now >= scheduled_time
            
        elif schedule.schedule_type == 'weekly':
            # รันทุกวันอาทิตย์
            if now.weekday() != 6:  # 6 = Sunday
                return False
            
            if last_run_thai.date() == now.date():
                return False  # รันแล้ววันนี้
            
            # เช็คว่าเวลาผ่านไปแล้วหรือยัง
            scheduled_time = now.replace(
                hour=schedule.time.hour,
                minute=schedule.time.minute,
                second=0,
                microsecond=0
            )
            return now >= scheduled_time
            
        elif schedule.schedule_type == 'monthly':
            # รันวันที่ 1 ของเดือน
            if now.day != 1:
                return False
            
            if last_run_thai.month == now.month and last_run_thai.year == now.year:
                return False  # รันแล้วเดือนนี้
            
            # เช็คว่าเวลาผ่านไปแล้วหรือยัง
            scheduled_time = now.replace(
                hour=schedule.time.hour,
                minute=schedule.time.minute,
                second=0,
                microsecond=0
            )
            return now >= scheduled_time
    
    else:
        # ยังไม่เคยรันเลย
        if schedule.schedule_type == 'daily':
            scheduled_time = now.replace(
                hour=schedule.time.hour,
                minute=schedule.time.minute,
                second=0,
                microsecond=0
            )
            return now >= scheduled_time
            
        elif schedule.schedule_type == 'weekly':
            return now.weekday() == 6  # วันอาทิตย์
            
        elif schedule.schedule_type == 'monthly':
            return now.day == 1  # วันที่ 1
    
    return False


def run_scheduled_backup(schedule, now):
    """รัน scheduled backup"""
    try:
        # Get PostgreSQL version
        pg_version = get_postgresql_version()
        
        # Create filename with timestamp and version (shorter format)
        timestamp = now.strftime('%y%m%d_%H%M')
        filename = f'bk_{timestamp}_pg{pg_version}_{schedule.environment[:3]}_sch.sql'
        
        # Create BackupHistory record
        backup_history = BackupHistory.objects.create(
            filename=filename,
            environment=schedule.environment,
            postgresql_version=pg_version,
            backup_type='scheduled',
            status='in_progress',
            progress=0,
            created_by=None,  # System initiated
            notes=f'Scheduled backup: {schedule.name}'
        )
        
        # Progress callback function
        def progress_callback(progress):
            backup_history.progress = progress
            backup_history.save()
        
        # Run pg_dump
        success = run_pg_dump(backup_history, progress_callback)
        
        if success:
            # Update schedule last_run
            schedule.last_run = now
            schedule.save()
            
            print(f'Scheduled backup completed: {filename}')
        else:
            print(f'Scheduled backup failed: {backup_history.notes}')
            
    except Exception as e:
        print(f'Error running scheduled backup: {e}')
