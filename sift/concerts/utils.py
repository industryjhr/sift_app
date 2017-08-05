"""
concerts/utils.py

Misc. utility functions for the concerts app:

* get_spotify_id
* make_artist_regex
"""

import logging, os

from .scrapers import (
    emptybottle,
    bottomlounge,
    subterranean,
    doubledoor,
    houseofblues,
    thaliahall,
    metro,
    lincolnhall,
    schubas,
)

logger = logging.getLogger('concerts')

# key is Venue objects's pk; used by scrape_shows mgmt command
SCRAPERS = {
    1: emptybottle.EmptyBottle,
    2: bottomlounge.BottomLounge,
    3: subterranean.Subterranean,
    4: doubledoor.DoubleDoor,
    5: houseofblues.HouseOfBlues,
    6: thaliahall.ThaliaHall,
    7: metro.Metro,
    8: lincolnhall.LincolnHall,
    9: schubas.SchubasTavern,
}

FIXTURES_BASE_DIR = os.path.join(
    os.environ.get('SIFT_HOME'),
    'concerts',
    'fixtures'
)

FIXTURE_DIRS = {
    'artists': os.path.join(FIXTURES_BASE_DIR, 'artists'),
    'concerts': os.path.join(FIXTURES_BASE_DIR, 'concerts'),
    'venues': os.path.join(FIXTURES_BASE_DIR, 'venues'),
}

def get_spotify_id(artist_name):
    """Returns Spotify artist ID, or empty string if none found."""

    import requests
    from django.utils.http import urlencode

    SPOTIFY_QUERY_BASE = 'https://api.spotify.com/v1/search?'
    spotify_token = os.environ.get('SPOTIFY_TOKEN')
    if spotify_token is None:
        import sys
        sys.exit("No SPOTIFY_TOKEN env var set. Sad!")

    # searching quoted artist name seems to give more accurate
    quoted_name = '\"' + artist_name + '\"'
    query_str = urlencode([('q', quoted_name), ('type', 'artist')])
    response = requests.get(
        SPOTIFY_QUERY_BASE + query_str,
        headers={"Authorization": "Bearer {}".format(spotify_token)}
    )
    response.raise_for_status()

    artist_id = ''

    try:
        artist_id = response.json()['artists']['items'][0]['id']
    except IndexError as e:
        logger.debug("Failed to get Spotify artist ID for {}".format(artist_name))

    return artist_id


def make_artist_regex(artist_name):
    """Returns regex string of artist name for storage in DB."""

    from string import punctuation
    import re

    PUNC_RE = re.compile(
        '[{}]'.format(punctuation),
        flags=re.I|re.M|re.DOTALL
    )

    no_punc = re.sub(PUNC_RE, r'.?', artist_name)
    no_end = re.sub(r'$', '\\\\b', no_punc)
    re_string = re.sub(r'^', '\\\\b', no_end)
    return re_string


if __name__ == '__main__':
    pass
