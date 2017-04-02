"""
concerts/management/commands/live_update.py

Regular job to refresh the site (Heroku deployment).

Deletes existing concert matches, then runs scrape_shows and make_matches
commmands to populate ConcertMatch table.
"""

from datetime import datetime
import logging
import sys

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from concerts.models import Concert


logger = logging.getLogger('concerts.data_management')


class Command(BaseCommand):
    help = 'Delete existing Concerts, scrapes venues, and finds the matches'

    def add_arguments(self, parser):
        parser.add_argument('--force',
            action='store_true',
            default=False,
            help='If True, overrides the date check and forces a refresh.'
        )


    def handle(self, *args, **options):

        # heroku scheduler jobs run at least every day;
        # only actually refresh every 10 or so
        date = datetime.today().day

        if not any((options['force'], not date % 7)):
            logger.info("Another day..")
            sys.exit()

        logger.info("Deleting existing Concert objects")
        Concert.objects.all().delete()

        logger.info("Scraping venue sites for concerts...")
        call_command('scrape_shows')
        logger.info("Finding target artists in the concert billings...")
        call_command('make_matches')

        # self.stdout.write("Done!")
