from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from manuals.models import Manual, ManualAttachment
import re
import os


class Command(BaseCommand):
    help = 'Clean up orphaned manual images from R2 storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Starting manual image cleanup...')
        
        # Get all manual content
        manuals = Manual.objects.all()
        used_images = set()
        
        # Extract all image URLs from manual content
        for manual in manuals:
            if manual.content:
                img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
                img_urls = re.findall(img_pattern, manual.content)
                
                for img_url in img_urls:
                    if '/manuals/images/' in img_url:
                        file_path = img_url.split('/manuals/images/')[-1]
                        full_path = f'manuals/images/{file_path}'
                        used_images.add(full_path)
        
        # Get all attachments
        attachments = ManualAttachment.objects.all()
        attachment_files = set()
        
        for attachment in attachments:
            if attachment.file:
                attachment_files.add(attachment.file.name)
        
        # Find orphaned files
        all_files = set()
        
        # List all files in manuals/images/ directory
        try:
            files = default_storage.listdir('manuals/images/')[1]  # Get files only
            for file in files:
                all_files.add(f'manuals/images/{file}')
        except Exception as e:
            self.stdout.write(f'Error listing files: {e}')
            return
        
        # Find orphaned files
        orphaned_files = all_files - used_images - attachment_files
        
        if not orphaned_files:
            self.stdout.write('No orphaned files found.')
            return
        
        self.stdout.write(f'Found {len(orphaned_files)} orphaned files:')
        
        for file_path in orphaned_files:
            self.stdout.write(f'  - {file_path}')
        
        if dry_run:
            self.stdout.write('Dry run completed. No files were deleted.')
            return
        
        # Delete orphaned files
        deleted_count = 0
        for file_path in orphaned_files:
            try:
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                    deleted_count += 1
                    self.stdout.write(f'Deleted: {file_path}')
                else:
                    self.stdout.write(f'File not found: {file_path}')
            except Exception as e:
                self.stdout.write(f'Error deleting {file_path}: {e}')
        
        self.stdout.write(f'Cleanup completed. Deleted {deleted_count} files.')
