from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from dbbackup.utils import run_pg_restore, get_backup_files
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Restore PostgreSQL database from backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Backup file to restore'
        )
        parser.add_argument(
            '--env',
            type=str,
            choices=['local', 'production'],
            required=True,
            help='Environment (local or production)'
        )
        parser.add_argument(
            '--mode',
            type=str,
            choices=['safe', 'drop'],
            default='safe',
            help='Restore mode: safe (default) or drop'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompts'
        )

    def handle(self, *args, **options):
        backup_file = options['file']
        environment = options['env']
        mode = options['mode']
        confirm = options['confirm']

        # Validate backup file
        if not os.path.exists(backup_file):
            raise CommandError(f'Backup file not found: {backup_file}')

        if not backup_file.endswith('.sql'):
            raise CommandError('Backup file must be a .sql file')

        # Show warning for drop mode
        if mode == 'drop':
            self.stdout.write(
                self.style.WARNING(
                    'WARNING: Drop mode will delete all existing data!'
                )
            )
            if not confirm:
                response = input('Are you sure you want to continue? (yes/no): ')
                if response.lower() != 'yes':
                    self.stdout.write('Restore cancelled')
                    return

        # Additional confirmation for production
        if environment == 'production':
            self.stdout.write(
                self.style.WARNING(
                    'WARNING: You are about to restore to PRODUCTION environment!'
                )
            )
            if not confirm:
                response = input('Type "RESTORE PRODUCTION" to confirm: ')
                if response != 'RESTORE PRODUCTION':
                    self.stdout.write('Restore cancelled')
                    return

        # Final confirmation
        if not confirm:
            self.stdout.write(f'Backup file: {backup_file}')
            self.stdout.write(f'Environment: {environment}')
            self.stdout.write(f'Mode: {mode}')
            response = input('Proceed with restore? (yes/no): ')
            if response.lower() != 'yes':
                self.stdout.write('Restore cancelled')
                return

        self.stdout.write(f'Starting restore from: {backup_file}')
        self.stdout.write(f'Environment: {environment}')
        self.stdout.write(f'Mode: {mode}')

        # Run restore
        success, message = run_pg_restore(backup_file, environment, mode)

        if success:
            self.stdout.write(
                self.style.SUCCESS(f'Restore completed successfully: {message}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Restore failed: {message}')
            )
            raise CommandError('Restore failed')
