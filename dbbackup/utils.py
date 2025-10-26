import os
import subprocess
import psycopg
from django.conf import settings
from django.db import connection
import pytz
from datetime import datetime


def get_postgresql_version():
    """ดึง PostgreSQL version จาก database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version_string = cursor.fetchone()[0]
            # Extract version number from string like "PostgreSQL 16.1 on x86_64-pc-linux-gnu..."
            version_parts = version_string.split()
            for part in version_parts:
                if part.startswith('16.') or part.startswith('15.') or part.startswith('14.'):
                    return part
            return "Unknown"
    except Exception as e:
        print(f"Error getting PostgreSQL version: {e}")
        return "Unknown"


def format_file_size(size_bytes):
    """แปลง bytes เป็น human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size = size_bytes
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def get_backup_filepath(environment):
    """สร้าง path ไฟล์ backup ตาม environment"""
    if environment == 'local':
        return settings.BACKUP_LOCAL_DIR
    else:
        return settings.BACKUP_PRODUCTION_DIR


def run_pg_dump(backup_history, progress_callback=None):
    """รัน pg_dump command พร้อมอัปเดต progress"""
    try:
        # Get database settings
        db_settings = settings.DATABASES['default']
        
        # Build pg_dump command
        cmd = [
            'pg_dump',
            '-h', db_settings['HOST'],
            '-p', str(db_settings['PORT']),
            '-U', db_settings['USER'],
            '-d', db_settings['NAME'],
            '--verbose',
            '--no-password'
        ]
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']
        
        # Create backup file path
        backup_dir = get_backup_filepath(backup_history.environment)
        backup_file = os.path.join(backup_dir, backup_history.filename)
        
        # Run pg_dump
        with open(backup_file, 'w') as f:
            process = subprocess.Popen(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )
            
            # Monitor progress (simplified - just check if process is running)
            while process.poll() is None:
                if progress_callback:
                    # Simulate progress (in real implementation, you'd parse pg_dump output)
                    current_progress = min(backup_history.progress + 10, 90)
                    progress_callback(current_progress)
                import time
                time.sleep(1)
            
            # Check if command was successful
            if process.returncode == 0:
                # Get file size
                file_size = os.path.getsize(backup_file)
                backup_history.file_size = file_size
                backup_history.status = 'completed'
                backup_history.progress = 100
                backup_history.save()
                return True
            else:
                error_output = process.stderr.read()
                backup_history.status = 'failed'
                backup_history.notes = f"pg_dump failed: {error_output}"
                backup_history.save()
                return False
                
    except Exception as e:
        backup_history.status = 'failed'
        backup_history.notes = f"Error running pg_dump: {str(e)}"
        backup_history.save()
        return False


def run_pg_restore(backup_file, environment, mode='safe'):
    """รัน psql/pg_restore command"""
    try:
        # Get database settings
        db_settings = settings.DATABASES['default']
        
        # Build psql command for restore
        cmd = [
            'psql',
            '-h', db_settings['HOST'],
            '-p', str(db_settings['PORT']),
            '-U', db_settings['USER'],
            '-d', db_settings['NAME'],
            '-f', backup_file,
            '--quiet'
        ]
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']
        
        # Run psql restore
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            env=env,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            return True, "Restore completed successfully"
        else:
            return False, f"Restore failed: {stderr}"
            
    except Exception as e:
        return False, f"Error running restore: {str(e)}"


def thai_datetime(dt):
    """แปลง datetime เป็นวันเดือนไทย พ.ศ. เวลาไทย"""
    if not dt:
        return "-"
    
    thai_tz = pytz.timezone('Asia/Bangkok')
    thai_time = dt.astimezone(thai_tz)
    buddhist_year = thai_time.year + 543
    
    thai_months = [
        'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
        'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
    ]
    
    month_name = thai_months[thai_time.month - 1]
    formatted_date = f"{thai_time.day} {month_name} {buddhist_year}, {thai_time.strftime('%H:%M')}"
    
    return formatted_date


def cleanup_old_backups(environment, keep_days=30):
    """ลบไฟล์ backup เก่าที่เกินกำหนด"""
    try:
        backup_dir = get_backup_filepath(environment)
        if not os.path.exists(backup_dir):
            return
        
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                if file_time < cutoff_time:
                    os.remove(file_path)
                    print(f"Deleted old backup: {filename}")
                    
    except Exception as e:
        print(f"Error cleaning up old backups: {e}")


def get_backup_files(environment):
    """ดึงรายการไฟล์ backup ทั้งหมด"""
    try:
        backup_dir = get_backup_filepath(environment)
        if not os.path.exists(backup_dir):
            return []
        
        files = []
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            if os.path.isfile(file_path) and filename.endswith('.sql'):
                file_size = os.path.getsize(file_path)
                file_time = os.path.getmtime(file_path)
                files.append({
                    'filename': filename,
                    'size': file_size,
                    'size_display': format_file_size(file_size),
                    'created_at': datetime.fromtimestamp(file_time),
                    'path': file_path
                })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created_at'], reverse=True)
        return files
        
    except Exception as e:
        print(f"Error getting backup files: {e}")
        return []
