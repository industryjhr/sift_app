"""
concerts/management/commands/get_spotify_artist_ids.py

For Artist entries without a spotify_id, queries the Spotify API for
artist ID and saves it to the DB.
"""

import logging
import time
from random import randint

from django.core.management.base import BaseCommand, CommandError
from django.utils.http import urlencode

import requests

from concerts.models import Artist

logger = logging.getLogger('concerts')

SPOTIFY_SEARCH_BASE = 'https://api.spotify.com/v1/search?'

class Command(BaseCommand):
    help = 'Attempt to save the Spotify Artist URI to the Artist model'

    def handle(self, *args, **options):

        for artist in Artist.objects.filter(is_active=True, spotify_id=''):

            # searching quoted artist name seems to give more accurate
            # first result; eg. Boris vs. "Boris"
            quoted_name = '\"' + artist.name + '\"'
            query_str = urlencode([('q', quoted_name), ('type', 'artist')])
            response = requests.get(SPOTIFY_SEARCH_BASE + query_str)
            response.raise_for_status()

            # use the artist regex algo on returned artist names to compare
            # to target? etc.

            if response.status_code == 200:
                time.sleep(randint(3,6))
                try:
                    artist_id = response.json()['artists']['items'][0]['id']
                    artist.spotify_id = artist_id
                    artist.save()
                except IndexError:
                    continue
            else:
                self.stdout.write(response.status_code + " - " + response.text)
                logger.debug(response.status_code + " - " + response.text)
