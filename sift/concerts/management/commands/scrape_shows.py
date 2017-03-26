"""
concerts/management/commands/scrape_shows.py

Using the concerts.utils.scrapers, scrapes venue sites and
writes the upcoming concerts to Concerts table.
"""

import logging

from django.core.management.base import BaseCommand, CommandError

from concerts.models import Venue, Concert
from concerts.utils import SCRAPERS


MISC_VENUE = Venue.objects.get(id=99)

logger = logging.getLogger('concerts.data_management')


class Command(BaseCommand):
    help = 'Scrapes sites for all active Venues and writes shows to Concerts table'

    def handle(self, *args, **options):

        for venue in Venue.objects.filter(is_active=True):
            # point to from model?
            scraper = SCRAPERS[venue.id]()

            logger.info("Scraping venue %s".format(venue))
            scraper.load_live_shows()

            for show in scraper.shows:
                # better to use venue.concert_set.create(...) ?
                concert = Concert.objects.create(
                    billing=show.artists,
                    venue=venue if show.venue_name==venue.name else MISC_VENUE,
                    date_time=show.show_date,
                    price=show.price,
                    url=show.show_url,
                )
                concert.save()
                logger.debug("Concert added: %s".format(concert))