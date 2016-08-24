"""
concerts/management/commands/refresh_heroku.py

Flushes and re-seeds the DB from Artist, Venue, and Concert fixtures,
then runs the make_matches management commmand to populate ConcertMatch table.

This workflow is currently necessary due to being unable to scrape the
Subterranean site from Heroku. cf. concerts/buffering_error.txt.
"""

import os, sys
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

FIXTURES_BASE_DIR = os.path.join(os.environ.get('SIFT_HOME'), 'concerts', 'fixtures')

FIXTURE_DIRS = {
    'artists': os.path.join(FIXTURES_BASE_DIR, 'artists'),
    'concerts': os.path.join(FIXTURES_BASE_DIR, 'concerts'),
    'venues': os.path.join(FIXTURES_BASE_DIR, 'venues'),
}

class Command(BaseCommand):
    help = "Flushes and re-seeds DB from fixtures, runs make_matches to find upcoming concerts."

    def handle(self, *args, **options):
        try:
            artists_fixtures = os.listdir(FIXTURE_DIRS['artists'])
            artists_fixtures.sort()
            latest_artists_fixture = os.path.join(
                FIXTURE_DIRS['artists'],
                artists_fixtures[-1]
            )

            venues_fixtures = os.listdir(FIXTURE_DIRS['venues'])
            venues_fixtures.sort()
            latest_venues_fixture = os.path.join(
                FIXTURE_DIRS['venues'],
                venues_fixtures[-1]
            )

            concerts_fixtures = os.listdir(FIXTURE_DIRS['concerts'])
            concerts_fixtures.sort()
            latest_concerts_fixture = os.path.join(
                FIXTURE_DIRS['concerts'],
                concerts_fixtures[-1]
            )
        except IndexError as e:
            sys.exit("Problem accessing a fixture: {}".format(e.args))

        self.stdout.write("Flushing DB...")
        call_command('flush', '--noinput')
        self.stdout.write("Loading artists from fixture...")
        call_command('loaddata', latest_artists_fixture)
        self.stdout.write("Loading venues from fixture...")
        call_command('loaddata', latest_venues_fixture)
        self.stdout.write("Loading concerts from fixture...")
        call_command('loaddata', latest_concerts_fixture)
        self.stdout.write("Making concert matches...")
        call_command('make_matches')
        self.stdout.write("Done!")
