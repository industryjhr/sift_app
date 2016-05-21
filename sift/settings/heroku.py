# settings/heroku.py
from .base import *

import dj_database_url


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', None)

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = os.environ.get('DEBUG', False)
DEBUG = False

#ALLOWED_HOSTS = []


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

#STATIC_URL = '/static/'
