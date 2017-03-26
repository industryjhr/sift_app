"""
concerts/management/commands/live_update.py

Regular job to refresh the site (Heroku deployment).

Deletes existing concert matches, then runs scrape_shows and make_matches
commmands to populate ConcertMatch table.
"""

import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from concerts.models import Concert


logger = logging.getLogger('concerts.data_management')


class Command(BaseCommand):
    help = 'Delete existing Concerts, scrapes venues, and finds the matches'

    def handle(self, *args, **options):

        logger.debug("Deleting existing Concert objects")
        Concert.objects.all().delete()

        self.stdout.write("Scraping venue sites for concerts...")
        call_command('scrape_shows')
        self.stdout.write("Finding target artists in the concert billings...")
        call_command('make_matches')

        # self.stdout.write("Done!")
