from .base import *

ALLOWED_HOSTS = ['www.lifesavingrankings.nl', 'lifesavingrankings.nl']
DEBUG = False

STATIC_URL = 'http://91.218.127.89:8000/static/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = ''
