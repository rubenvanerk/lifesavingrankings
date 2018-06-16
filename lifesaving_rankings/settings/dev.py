from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['d9njmvozw5.execute-api.eu-central-1.amazonaws.com']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATIC_URL = 'http://zappa-tzjq522h5.s3-website.eu-central-1.amazonaws.com/static/'
