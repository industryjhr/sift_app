"""
concerts/management/commands/live_update.py

Regular job to refresh the site (Heroku deployment).

Deletes existing concert matches, then runs scrape_shows and make_matches
commmands to populate ConcertMatch table.
"""

import logging, os, sys
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from concerts.models import Concert
from concerts.utils import FIXTURE_DIRS


logger = logging.getLogger('concerts.data_management')


class Command(BaseCommand):
    help = 'Flushes DB, reloads artist and venue fixtures, scrapes shows and finds the matches'

    def handle(self, *args, **options):

        logger.info("TESTING LOGGING")

        # self.stdout.write("Done!")
