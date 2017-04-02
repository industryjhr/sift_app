# settings/heroku.py
import os

from .base import *

import dj_database_url


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', None)

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = os.environ.get('DEBUG', False)
DEBUG = bool(os.environ.get('DEBUG', False))

ALLOWED_HOSTS = ['sift.herokuapp.com']

SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTP_ONLY = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 3600 # could be longer
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
X_FRAME_OPTIONS = 'DENY'

MIDDLEWARE_CLASSES.append('rollbar.contrib.django.middleware.RollbarNotifierMiddleware')

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('HEROKU_POSTGRESQL_CYAN_URL'))
}

# Logging
# Heroku captures logstream from stdout and stderr
# https://devcenter.heroku.com/articles/logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            # 'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console_verbose': {
            'level': 'DEBUG',
            # 'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # 'concerts': {
        #     'handlers': ['console'],
        #     'level': 'INFO',
        #     'propogate': True,
        # },
        'concerts.data_management': {
            'handlers': ['console_verbose'],
            'level': 'INFO',
            'propogate': False,
        },
    }
}


# Rollbar
ROLLBAR = {
    'access_token': os.environ.get('ROLLBAR_ACCESS_TOKEN'),
    'environment': 'production',
    'branch': 'master',
    'root': BASE_DIR,
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

#STATIC_URL = '/static/'
