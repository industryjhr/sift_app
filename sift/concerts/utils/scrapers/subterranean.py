import calendar, datetime, iso8601, os, pytz, sys, time
from collections import namedtuple

import requests
from bs4 import BeautifulSoup as bs

from .venue import Venue

TODAY = datetime.datetime.today()

class Subterranean(Venue):
    """
    Scraper object for Subterranean.

    2011 W North Ave.
    Chicago, IL, 60647
    http://www.subt.net
    """

    def __init__(self):
        super().__init__()
        self.venue_name = 'Subterranean'
        self.url = 'http://www.subt.net'

    def get_summaries(self, html):
        """
        See Venue.get_summaries.

        html dump > '.list-view-item'
        """

        show_summaries = bs(html, 'html.parser').select('.list-view-item')
        return show_summaries

    def get_artist_billing(self, summary):
        """
        See Venue.get_artist_billing.

        '.list-view-item' > '.list-view-details' > '.headliners'
        '.list-view-item' > '.list-view-details' > '.supports'
        """

        # headlining and support acts in separate tags; supporting acts optional
        headliners = summary.select('.list-view-details > .headliners')[0].text
        try:
            support = summary.select('.list-view-details > .supports')[0].text
        except IndexError:
            return headliners

        return headliners + ' with ' + support


    def get_venue_info(self, summary):
        """
        See Venue.get_venue_info.

        Subterranean concerts are in-house only so far.
        """

        venue_name = self.venue_name
        venue_id = self.venue_id

        return (venue_name, venue_id)


    def get_show_date(self, summary):
        """
        See Venue.get_show_date.

        '.list-view-item' > '.value-title' > 'title' attribute
        """

        show_iso = summary.select('.value-title')[0].attrs['title']
        local_datetime = iso8601.parse_date(show_iso)
        return local_datetime.astimezone(pytz.utc)

    def get_show_price(self, summary):
        """
        See Venue.get_artist_billing.

        '.list-view-item' > '.price-range'
        """

        try:
            price = summary.select('.price-range')[0].text.strip()
        except IndexError:
            price = 'No price / free?'
        return price

    def get_show_url(self, summary):
        """
        See Venue.get_artist_billing.

        '.list-view-item' > first link
        """

        show_page = summary.find('a', href=True)['href']
        # show_page link relative
        return self.url + show_page