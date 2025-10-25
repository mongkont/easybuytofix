from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'บัญชีผู้ใช้'
    
    def ready(self):
        """Import signals when app is ready"""
        import accounts.signals