from .base import *

ALLOWED_HOSTS = ['www.lifesavingrankings.nl',
                 'lifesavingrankings.nl',
                 'www.lifesavingrankings.com',
                 'lifesavingrankings.com',
                 'b6ip9znscb.execute-api.eu-central-1.amazonaws.com']
DEBUG = False

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = env('STATIC_AWS_ID')
AWS_SECRET_ACCESS_KEY = env('STATIC_AWS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')

# AWS_S3_CUSTOM_DOMAIN = 'rankings-production-static.s3.amazonaws.com'
# STATIC_URL = 'https://rankings-production-static.s3.eu-central-1.amazonaws.com/javascript/main.js/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('SMTP_HOST')
EMAIL_HOST_USER = env('SMTP_USER')
EMAIL_HOST_PASSWORD = env('SMTP_PASSWORD')
EMAIL_PORT = env('SMTP_PORT')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'ruben@lifesavingrankings.com'
SERVER_EMAIL = 'ruben@lifesavingrankings.com'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[LifesavingRankings.com] '