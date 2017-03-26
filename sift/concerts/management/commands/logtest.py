"""
concerts/management/commands/logtest.py

Testing logging on Heroku..
"""

import logging, os, sys
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError


logger = logging.getLogger('concerts.data_management')


class Command(BaseCommand):
    help = 'Test logging on Heroku'

    def handle(self, *args, **options):

        logger.info("Testing logging ({})".format(logger))
        self.stdout.write("Logging test done. (self.stdout.write)")
