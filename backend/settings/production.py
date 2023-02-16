import os

from backend.settings.base import *

DEBUG = True

ALLOWED_HOSTS = [
    "https://usc-dating-club.herokuapp.com",
    "https://usc-dating-club-test.herokuapp.com",
]

CORS_ALLOWED_ORIGINS = [
    "https://usc-dating-club.herokuapp.com",
    "https://usc-dating-club-test.herokuapp.com",
]

import django_heroku
django_heroku.settings(locals())

import dj_database_url
DATABASES = {'default': dj_database_url.config(conn_max_age=600)}

# TODO: Pictures
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 
MEDIA_URL = '/media/'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_REGION_NAME = "us-west-1"
AWS_STORAGE_BUCKET_NAME = os.environ.get('S3_BUCKET')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'