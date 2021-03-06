# -*- coding: utf-8 -*-
# concerts/scrapers/thaliahall.py

import calendar, datetime, iso8601, os, pytz, sys, time
from collections import namedtuple

import requests
from bs4 import BeautifulSoup as bs

from .venue import Venue

TODAY = datetime.datetime.today()

class ThaliaHall(Venue):
    """
    Scraper object for Thalia Hall.

    1807 S. Allport St. 
    Chicago, IL 60608
    http://thaliahallchicago.com/
    """

    def __init__(self):
        super().__init__()
        self.venue_name = 'Thalia Hall'
        self.url = 'http://thaliahallchicago.com/'

    def get_summaries(self, html):
        """
        See Venue.get_summaries.

        html dump > '.event-list-item-inner'
        """

        show_summaries = bs(html, 'html.parser').select('.event-list-item-inner')
        return show_summaries


    def get_artist_billing(self, summary):
        """
        See Venue.get_artist_billing.

        show_summary > '.tw-event-name'
        """

        artists_blob = summary.select('.tw-event-name')[0].text
        stripped = artists_blob.strip()

        return stripped


    def get_venue_info(self, summary):
        """
        See Venue.get_venue_info.

        External venues indicated in an image; Thalia Hall by default.
        """

        # TODO remove deprecated self.venue_id from parent
        return (self.venue_name, self.venue_id)


    def get_show_date(self, summary):
        """
        See Venue.get_show_date.

        show_summary > '.tw-event-date'
        show_summary > '.tw-event-time'
        """

        DATE_STRING_FORMAT = "%B %d, %Y"

        date_on_site = summary.select('.tw-event-date')[0].text.strip()
        show_datetime_obj = time.strptime(date_on_site, DATE_STRING_FORMAT)
        show_year = show_datetime_obj.tm_year
        show_month = show_datetime_obj.tm_mon
        show_date = show_datetime_obj.tm_mday

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

        show_summary > '.tw-event-price'
        """

        price = summary.select('.tw-event-price')[0].text.strip()
        return price


    def get_show_url(self, summary):
        """
        See Venue.get_show_url.

        '.show_summary' > first link
        """

        show_url = summary.find('a', href=True)['href']
        return show_url