from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from dbbackup.models import BackupHistory, BackupSchedule
from dbbackup.utils import (
    get_postgresql_version, 
    get_backup_files, 
    run_pg_dump, 
    run_pg_restore,
    thai_datetime
)
import json
import threading
import os

User = get_user_model()


@staff_member_required
def backup_view(request):
    """หน้า backup database"""
    if request.method == 'POST':
        environment = request.POST.get('environment')
        notes = request.POST.get('notes', '')
        
        if not environment:
            return JsonResponse({'success': False, 'error': 'กรุณาเลือก environment'})
        
        # Get PostgreSQL version
        pg_version = get_postgresql_version()
        
        # Create filename with timestamp and version (shorter format)
        timestamp = timezone.now().strftime('%y%m%d_%H%M')
        filename = f'bk_{timestamp}_pg{pg_version}_{environment[:3]}.sql'
        
        # Create BackupHistory record
        backup_history = BackupHistory.objects.create(
            filename=filename,
            environment=environment,
            postgresql_version=pg_version,
            backup_type='manual',
            status='in_progress',
            progress=0,
            created_by=request.user,
            notes=notes
        )
        
        # Run backup in background thread
        def run_backup():
            def progress_callback(progress):
                backup_history.progress = progress
                backup_history.save()
            
            success = run_pg_dump(backup_history, progress_callback)
            
            if not success:
                backup_history.status = 'failed'
                backup_history.save()
        
        thread = threading.Thread(target=run_backup)
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'success': True, 
            'backup_id': backup_history.id,
            'message': 'เริ่ม backup แล้ว กรุณารอสักครู่'
        })
    
    # GET request - show backup form
    pg_version = get_postgresql_version()
    context = {
        'postgresql_version': pg_version,
    }
    return render(request, 'admin/dbbackup/backup_form.html', context)


@staff_member_required
def restore_view(request):
    """หน้า restore database"""
    if request.method == 'POST':
        backup_file = request.POST.get('backup_file')
        environment = request.POST.get('environment')
        mode = request.POST.get('mode', 'safe')
        confirmation = request.POST.get('confirmation')
        
        if not all([backup_file, environment]):
            return JsonResponse({'success': False, 'error': 'กรุณากรอกข้อมูลให้ครบถ้วน'})
        
        # Validate confirmation
        if mode == 'drop' and confirmation != 'DROP':
            return JsonResponse({'success': False, 'error': 'กรุณาพิมพ์ DROP เพื่อยืนยัน'})
        
        if environment == 'production' and confirmation != 'RESTORE PRODUCTION':
            return JsonResponse({'success': False, 'error': 'กรุณาพิมพ์ RESTORE PRODUCTION เพื่อยืนยัน'})
        
        # Check if backup file exists
        if not os.path.exists(backup_file):
            return JsonResponse({'success': False, 'error': 'ไม่พบไฟล์ backup'})
        
        # Run restore
        success, message = run_pg_restore(backup_file, environment, mode)
        
        if success:
            return JsonResponse({'success': True, 'message': message})
        else:
            return JsonResponse({'success': False, 'error': message})
    
    # GET request - show restore form
    local_files = get_backup_files('local')
    production_files = get_backup_files('production')
    
    context = {
        'local_files': local_files,
        'production_files': production_files,
    }
    return render(request, 'admin/dbbackup/restore_form.html', context)


@staff_member_required
def progress_api(request, backup_id):
    """API endpoint สำหรับดึง progress ของ backup"""
    try:
        backup = get_object_or_404(BackupHistory, id=backup_id)
        
        return JsonResponse({
            'status': backup.status,
            'progress': backup.progress,
            'message': backup.notes or ''
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def download_backup(request, backup_id):
    """ดาวน์โหลดไฟล์ backup"""
    backup = get_object_or_404(BackupHistory, id=backup_id)
    
    if not backup.file_exists:
        messages.error(request, 'ไม่พบไฟล์ backup')
        return HttpResponse('File not found', status=404)
    
    try:
        with open(backup.file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename="{backup.filename}"'
            return response
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาดในการดาวน์โหลด: {e}')
        return HttpResponse('Download error', status=500)


@staff_member_required
def delete_backup(request, backup_id):
    """ลบไฟล์ backup"""
    backup = get_object_or_404(BackupHistory, id=backup_id)
    
    try:
        if backup.file_exists:
            os.remove(backup.file_path)
        
        backup.delete()
        messages.success(request, f'ลบ backup {backup.filename} เรียบร้อยแล้ว')
        
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาดในการลบ: {e}')
    
    return JsonResponse({'success': True})