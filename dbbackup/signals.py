from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import BackupHistory
import os


@receiver(post_delete, sender=BackupHistory)
def delete_backup_file_on_delete(sender, instance, **kwargs):
    """ลบไฟล์ backup เมื่อลบ BackupHistory record"""
    try:
        if instance.file_exists:
            os.remove(instance.file_path)
            print(f"Deleted backup file: {instance.filename}")
    except Exception as e:
        print(f"Error deleting backup file {instance.filename}: {e}")
