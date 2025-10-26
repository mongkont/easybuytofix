from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from dbbackup.models import BackupHistory
from dbbackup.utils import get_postgresql_version, run_pg_dump
from datetime import datetime
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Backup PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--env',
            type=str,
            choices=['local', 'production'],
            required=True,
            help='Environment (local or production)'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID who initiated the backup'
        )
        parser.add_argument(
            '--notes',
            type=str,
            help='Notes for the backup'
        )

    def handle(self, *args, **options):
        environment = options['env']
        user_id = options.get('user_id')
        notes = options.get('notes', '')

        # Get user if provided
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'User with ID {user_id} not found')
                )

        # Get PostgreSQL version
        pg_version = get_postgresql_version()
        self.stdout.write(f'PostgreSQL Version: {pg_version}')

        # Create filename with timestamp and version (shorter format)
        timestamp = datetime.now().strftime('%y%m%d_%H%M')
        filename = f'bk_{timestamp}_pg{pg_version}_{environment[:3]}.sql'

        # Create BackupHistory record
        backup_history = BackupHistory.objects.create(
            filename=filename,
            environment=environment,
            postgresql_version=pg_version,
            backup_type='manual',
            status='in_progress',
            progress=0,
            created_by=user,
            notes=notes
        )

        self.stdout.write(f'Starting backup: {filename}')
        self.stdout.write(f'Environment: {environment}')
        self.stdout.write(f'Status: {backup_history.status}')

        # Progress callback function
        def progress_callback(progress):
            backup_history.progress = progress
            backup_history.save()
            self.stdout.write(f'Progress: {progress}%')

        # Run pg_dump
        success = run_pg_dump(backup_history, progress_callback)

        if success:
            self.stdout.write(
                self.style.SUCCESS(f'Backup completed successfully: {filename}')
            )
            self.stdout.write(f'File size: {backup_history.file_size_display}')
        else:
            self.stdout.write(
                self.style.ERROR(f'Backup failed: {backup_history.notes}')
            )
            raise CommandError('Backup failed')

        return str(backup_history.id)
