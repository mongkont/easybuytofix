from django.apps import AppConfig


class DbbackupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dbbackup'
    verbose_name = 'ระบบ Backup Database'
    
    def ready(self):
        import dbbackup.signals