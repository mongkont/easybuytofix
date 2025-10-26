from django.urls import path
from . import views

app_name = 'dbbackup'

urlpatterns = [
    path('backup/', views.backup_view, name='backup'),
    path('restore/', views.restore_view, name='restore'),
    path('progress/<int:backup_id>/', views.progress_api, name='progress'),
    path('<int:backup_id>/download/', views.download_backup, name='download'),
    path('<int:backup_id>/delete/', views.delete_backup, name='delete'),
]
