from storages.backends.s3boto3 import S3Boto3Storage
import os
from django.conf import settings


class ManualMediaStorage(S3Boto3Storage):
    """Custom storage backend for Manual attachments to ensure R2 uploads"""
    location = 'manuals/images'
    file_overwrite = False
    default_acl = 'public-read'
    
    def __init__(self, *args, **kwargs):
        # Only use R2 if enabled
        if os.getenv('R2_ENABLED', 'False').lower() == 'true':
            kwargs.update({
                'endpoint_url': os.getenv('R2_ENDPOINT_URL'),
                'aws_access_key_id': os.getenv('R2_ACCESS_KEY_ID'),
                'aws_secret_access_key': os.getenv('R2_SECRET_ACCESS_KEY'),
                'bucket_name': os.getenv('R2_BUCKET_NAME'),
                'custom_domain': os.getenv('R2_CUSTOM_DOMAIN'),
            })
        super().__init__(*args, **kwargs)
