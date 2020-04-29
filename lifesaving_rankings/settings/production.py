from .base import *

ALLOWED_HOSTS = ['staging.lifesavingrankings.com',
                 'www.lifesavingrankings.nl',
                 'lifesavingrankings.nl',
                 'www.lifesavingrankings.com',
                 'lifesavingrankings.com']
DEBUG = False

# static files over s3 settings
STATIC_S3_BUCKET = env('AWS_STORAGE_BUCKET_NAME')
STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"
AWS_S3_BUCKET_NAME_STATIC = STATIC_S3_BUCKET
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % STATIC_S3_BUCKET
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

# email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('SMTP_HOST')
EMAIL_HOST_USER = env('SMTP_USER')
EMAIL_HOST_PASSWORD = env('SMTP_PASSWORD')
EMAIL_PORT = env('SMTP_PORT')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'ruben@lifesavingrankings.com'
SERVER_EMAIL = 'ruben@lifesavingrankings.com'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[LifesavingRankings.com] '