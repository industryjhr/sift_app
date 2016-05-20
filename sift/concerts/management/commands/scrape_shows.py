from django.core.management.base import BaseCommand, CommandError
from shows.models import Venue, Concert
from shows.utils import SCRAPERS


class Command(BaseCommand):
    help = 'Scrapes sites for all active venues and writes shows to Concerts table'

    def handle(self, *args, **options):
        misc_venue = Venue.objects.get(id=99)

        for venue in Venue.objects.filter(is_active=True):
            scraper = SCRAPERS[venue.id]
            scraper.load_live_shows()

            for show in scraper.shows:
                # better to use venue.concert_set.create(...) ?
                concert = Concert.objects.create(
                    billing=show.artists,
                    venue=venue if show.venue_name==venue.name else misc_venue,
                    date_time=show.show_date,
                    price=show.price,
                    url=show.show_url,
                )
                concert.save()
