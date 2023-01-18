import os

from backend.settings.base import *

DEBUG = False

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