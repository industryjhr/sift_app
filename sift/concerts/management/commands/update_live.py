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
        # try:
        #     artists_fixtures = os.listdir(FIXTURE_DIRS['artists'])
        #     artists_fixtures.sort()
        #     latest_artists_fixture = os.path.join(
        #         FIXTURE_DIRS['artists'],
        #         artists_fixtures[-1]
        #     )

        #     venues_fixtures = os.listdir(FIXTURE_DIRS['venues'])
        #     venues_fixtures.sort()
        #     latest_venues_fixture = os.path.join(
        #         FIXTURE_DIRS['venues'],
        #         venues_fixtures[-1]
        #     )

        #     concerts_fixtures = os.listdir(FIXTURE_DIRS['concerts'])
        #     concerts_fixtures.sort()
        #     latest_concerts_fixture = os.path.join(
        #         FIXTURE_DIRS['concerts'],
        #         concerts_fixtures[-1]
        #     )
        # except IndexError as e:
        #     sys.exit("Problem opening a fixture: {}".format(e.args))

        # self.stdout.write("Flushing DB...")
        # call_command('flush', '--noinput')

        logger.debug("Deleting existing Concert objects")
        Concert.objects.all().delete()

        # self.stdout.write("Loading artists from fixture...")
        # call_command('loaddata', latest_artists_fixture)
        # self.stdout.write("Loading venues from fixture...")
        # call_command('loaddata', latest_venues_fixture)


        self.stdout.write("Scraping venue sites for concerts...")
        call_command('scrape_shows')
        # logger.info("Would scrape shows here")
        self.stdout.write("Finding target artists in the concert billings...")
        # logger.info("Would make matches here")
        call_command('make_matches')


        # TODO Add concert fixture rotation?
        # concert_fixture_name = datetime.utcnow().strftime('%Y%m%d') + '_concert.json'
        # concert_fixture_path = os.path.join(FIXTURE_DIRS['concerts'], concert_fixture_name)
        # self.stdout.write("Dumping new concerts to {}".format(concert_fixture_name))
        # call_command(
        #     'dumpdata',
        #     'concerts.Concert',
        #     '--indent=4',
        #     '--output={}'.format(concert_fixture_path)
        # )
        self.stdout.write("Done!")
