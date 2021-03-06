"""
WSGI config for sift project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import logging
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sift.settings.heroku")

# adding this didn't send logs to heroku handler
#logging.basicConfig(
#    level=logging.INFO,
#    format='%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
#)

application = get_wsgi_application()
