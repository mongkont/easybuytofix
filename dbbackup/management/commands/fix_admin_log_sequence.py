from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.admin.models import LogEntry
from django.db import models


class Command(BaseCommand):
    help = 'Fix django_admin_log sequence issue'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Get current sequence value
            cursor.execute("SELECT last_value FROM django_admin_log_id_seq")
            current_seq = cursor.fetchone()[0]
            
            # Get max ID from table
            max_id = LogEntry.objects.aggregate(max_id=models.Max('id'))['max_id']
            
            self.stdout.write(f"Current sequence value: {current_seq}")
            self.stdout.write(f"Max ID in table: {max_id}")
            
            if current_seq <= max_id:
                # Reset sequence to max_id + 1
                new_seq = max_id + 1
                cursor.execute(f"SELECT setval('django_admin_log_id_seq', {new_seq})")
                self.stdout.write(f"Reset sequence to: {new_seq}")
                self.stdout.write(
                    self.style.SUCCESS('Successfully fixed django_admin_log sequence!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Sequence is already correct!')
                )
