"""
concerts/management/commands/make_matches.py

Uses the Artist.re_string to search for the artist in the
concert lineup (Concert.billing).  If a match is found, saves a
ConcertMatch object for lookup later.
"""

import re
import logging

from django.core.management.base import BaseCommand, CommandError
from concerts.models import Artist, Concert, ConcertMatch, Venue


logger = logging.getLogger('concerts.data_management')


class Command(BaseCommand):
    help = 'Looks for tracked artists in the concert billings and saves matches'

    def handle(self, *args, **options):
        artist_pairs = list(Artist.objects.filter(is_active=True).values_list('id', 're_string'))
        concert_pairs = list(Concert.objects.filter(is_active=True).values_list('id', 'billing'))

        for artist_id, regex_string in artist_pairs:
            artist_regex = re.compile(
                r'{}'.format(regex_string),
                flags=re.IGNORECASE|re.MULTILINE|re.DOTALL,
            )

            for concert_id, concert_billing in concert_pairs:
                if artist_regex.search(concert_billing):
                    concert_matched = Concert.objects.get(id=concert_id)
                    artist_matched = Artist.objects.get(id=artist_id)
                    logger.info(
                        "Matched artist {} and concert {}".format(
                            artist_matched, concert_matched
                        )
                    )
                    # check for existing concertmatch
                    # TODO but hacky? --review models--

                    match, created = ConcertMatch.objects.get_or_create(
                        concert=concert_matched
                    )

                    concert_matched.artists.add(artist_matched)
                    concert_matched.save()
                    match.artists.add(artist_matched)
                    match.save()

# on first match, create entry in ConcertMatch, add artist to Concert.artists
# subsequent matches add artist to ConcertMatch.artists, Concert.artists
