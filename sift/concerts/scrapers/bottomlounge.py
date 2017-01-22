# -*- coding: utf-8 -*-
# concerts/scrapers/bottomlounge.py

from .venue import Venue

import calendar, datetime, iso8601, os, pytz, sys, time
from collections import namedtuple

import requests
from bs4 import BeautifulSoup as bs

TODAY = datetime.datetime.today()


class BottomLounge(Venue):
    """
    Scraper object for Bottom Lounge.

    1375 W Lake St.
    Chicago, IL, 60607
    http://bottomlounge.com
    """

    def __init__(self):
        super().__init__()
        self.venue_name = 'Bottom Lounge'
        self.url = 'http://bottomlounge.com/events'


    def get_summaries(self, html):
        """
        See Venue.get_summaries.

        html dump > '.schedule-item-content'
        """

        show_summaries = bs(html, 'html.parser').select('.schedule-item-content')
        return show_summaries


    def get_artist_billing(self, summary):
        """
        See Venue.get_artist_billing.

        '.schedule-item-content' > '.schedule-title' (All one element)
        """

        # artist billing as one string; could break down on ' * '
        artists = summary.select('.schedule-title')[0].text

        return artists


    def get_venue_info(self, summary):
        """
        See Venue.get_venue_info.

        Bottom Lounge appears currently to promote in-house shows only.
        """

        # BL seems to promote in-house shows only
        venue_name = self.venue_name
        # TODO remove venue_id logic
        venue_id = 99

        return (venue_name, venue_id)


    def get_show_date(self, summary):
        """
        See Venue.get_show_date.

        '.schedule-item-content' > '.schedule-date' >

            span[0]: '09/08/2016'
            span[1]: ' Doors 6:00 PM    Show 6:30 PM'

        Use show time.
        """

        dt_spans = summary.select('.schedule-date')[0].find_all('span')
        show_month, show_date, show_year = tuple(dt_spans[0].text.split('/'))

        # use show time
        html_time = ' '.join(dt_spans[1].text.split()[-2:])
        # Rarely, a show on the site doesn't have AM/PM, eg. 'Show 6:00'.
        # In such cases, assume it's PM.
        if html_time.split()[0].isalpha():
            html_time = '{} PM'.format(html_time.split()[1])

        # convert str to 24hr
        try:
            t = time.strptime(html_time, '%I:%M %p')
        except ValueError:
            # XXX actually handle this
            t = time.strptime('12:12 PM', '%I:%M %p')

        utc_datetime = Venue.make_utc_datetime(
            show_year=int(show_year),
            show_month=int(show_month),
            show_day=int(show_date),
            show_hour=t.tm_hour,
            show_minute=t.tm_min
        )

        return utc_datetime


    def get_show_price(self, summary):
        """
        See Venue.get_show_price.

        BL prices only available through TicketWeb
        """

        price = '(See ticketing site for price)'
        return price


    def get_show_url(self, summary):
        """
        See Venue.get_show_url.

        '.schedule-item-content' > first link
        """

        show_url = summary.find('a', href=True)['href']
        return show_url
