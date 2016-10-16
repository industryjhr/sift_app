import calendar, datetime, iso8601, os, pytz, sys, time
from collections import namedtuple

import requests
from bs4 import BeautifulSoup as bs

from .venue import Venue

TODAY = datetime.datetime.today()

class EmptyBottle(Venue):
    """
    Scraper object for The Empty Bottle.

    1035 N Western Ave.
    Chicago, IL, 60622
    http://emptybottle.com
    """

    def __init__(self):
        super().__init__()
        self.venue_name = 'The Empty Bottle'
        self.url = 'http://emptybottle.com'

    def get_summaries(self, html):
        """
        See Venue.get_summaries.

        html dump > '.show_summary'
        """

        show_summaries = bs(html, 'html.parser').select('.show_summary')
        return show_summaries


    def get_artist_billing(self, summary):
        """
        See Venue.get_artist_billing.

        '.show_summary' > '.show_artists'
        """

        artists_blob = summary.select('.show_artists')[0].text
        stripped = artists_blob.strip()
        formatted = stripped.replace(' \n', ',')

        return formatted


    def get_venue_info(self, summary):
        """
        See Venue.get_venue_info.

        If show is at an alternate venue:
            '.show_summary' > '.show_venue'
        
        Else Empty Bottle.
        """

        if summary.select('.show_venue'):
            venue_name = summary.select('.show_venue')[0].text.strip()
            venue_id = 99
        else:
            venue_name = self.venue_name
            venue_id = self.venue_id

        return (venue_name, venue_id)


    def get_show_date(self, summary):
        """
        See Venue.get_show_date.

        '.show_summary' > '.tw-event-date'
        '.show_summary' > '.tw-event-time'
        """

        # Dates on EB site use abbreviations, conform to calendar.month_abbr
        month_map = {k:v for v, k in enumerate(calendar.month_abbr)}

        date_on_site = summary.select('.tw-event-date')[0].text
        # month as number (1-12)
        show_month = month_map[date_on_site.split()[0]]
        show_date = int(date_on_site.split()[1])
        if show_month >= TODAY.month:
            show_year = TODAY.year
        else:
            show_year = TODAY.year + 1

        html_time = summary.select('.tw-event-time')[0].text
        t = time.strptime(html_time, '%I:%M %p')

        utc_datetime = Venue.make_utc_datetime(
            show_year=int(show_year),
            show_month=int(show_month),
            show_day=int(show_date),
            show_hour=t.tm_hour,
            show_minute=t.tm_min)

        return utc_datetime


    def get_show_price(self, summary):
        """
        See Venue.get_show_price.

        '.show_summary' > '.show_price'
        """

        price = summary.select('.show_price')[0].text.strip()
        return price


    def get_show_url(self, summary):
        """
        See Venue.get_show_url.

        '.show_summary' > first link
        """

        show_url = summary.find('a', href=True)['href']
        return show_url