# -*- coding: utf-8 -*-

"""
concerts/scrapers/venue.py

Class definition for Venue base class.
"""

import calendar, datetime, iso8601, os, pytz, sys, time
from collections import namedtuple

import requests
from bs4 import BeautifulSoup as bs

TODAY = datetime.datetime.today()

ShowTuple = namedtuple(
                'show',
                'artists, venue_name, show_date, price, show_url, schedule_url'
            )


class Venue:
    """
    Base class for venue scrapers to inherit from.

    The base class defines a `shows` data attribute, initialized as an empty
    list.  The child venue classes should also define venue_name
    and url data attributes.

    Complete methods include make_shows, load_live_shows, and
    (staticmethod) make_utc_datetime.

    The rest of the methods are venue-specific parsing functions, to be
    defined by child objects.
    """

    show_fac = ShowTuple

    # TODO remove venue_id logic, now tracked in models
    def __init__(self, **kwargs):
        self.shows = []
        self.venue_id = 99

    def __str__(self):
        return "{0} -- {1} current shows".format(
            self.venue_name, len(self.shows)
        )


    def get_summaries(self, html):
        """
        Venue-specific parsing function.  Returns list of parent beautifulsoup
        elements for shows.

        :param str html: The scraped HTML of the venue's concert schedule page.
        :returns: A list of show "summaries" -- parent bs elements that contain
                  all sub-elements with relevant information for a concert.
        """
        raise NotImplementedError("get_summaries is venue-specific")


    def get_artist_billing(self, summary):
        """
        Venue-specific parsing function.  Extracts and returns artist billing
        for a concert.

        :param bs4.element.Tag summary: HTML blob for one concert.
        :returns: A string containing all artists for the concert.
        """
        raise NotImplementedError("get_artist_billing is venue-specific")


    def get_venue_info(self, summary):
        """
        Venue-specific parsing function.  Extracts and returns the venue
        details for a concert.  Done on a per-concert basis because some venues
        may hold/produce concerts at other locations (currently tracked in the
        DB under venue.id 99).

        :param bs4.element.Tag summary: HTML blob for one concert.
        :returns: A tuple of (<venue name>, <venue id>) for the concert.
        """
        raise NotImplementedError("get_venue_info is venue-specific")


    def get_show_date(self, summary):
        """
        Venue-specific parsing function.  Extracts and returns a UTC datetime
        object for a concert.

        :param bs4.element.Tag summary: HTML blob for one concert.
        :returns: UTC datetime object.
        """
        raise NotImplementedError("get_show_date is venue-specific")

    @staticmethod
    def make_utc_datetime(**kwargs):
        """
        Helper function to convert the local (Chicago) time as scraped
        to a UTC datetime object.

        Expected in the kwargs:

        :param int year: Year of the concert start time.
        :param int month: Month of the concert start time.
        :param int day: Day of the concert start time.
        :param int hour: Hour of the concert start time.
        :param int minute: Minute of the concert start time.
        :returns: UTC datetime object.
        """

        naive_time_obj = datetime.datetime(
            year=kwargs['show_year'],
            month=kwargs['show_month'],
            day=kwargs['show_day'],
            hour=kwargs['show_hour'],
            minute=kwargs['show_minute'],
        )

        chicago_tz = pytz.timezone('US/Central')
        utc_tz = pytz.timezone('UTC')

        localized = chicago_tz.localize(naive_time_obj)
        utc_time = localized.astimezone(utc_tz)
        return utc_time


    def get_show_price(self, summary):
        """
        Venue-specific parsing function.  Extracts and returns a string
        describing the ticket price, due to variations.

        :param bs4.element.Tag summary: HTML blob for one concert.
        :returns: ticket price info (as string) for the concert.
        """
        raise NotImplementedError("get_show_price is venue-specific")


    def get_show_url(self, summary):
        """
        Venue-specific parsing function.  Extracts and returns a URL
        to the concert page on the venue's official site.

        :param bs4.element.Tag summary: HTML blob for one concert.
        :returns: a URL string to the concert page on the venue's site.
        """
        raise NotImplementedError("get_show_url is venue-specific")


    def make_shows(self, html):
        """
        Venue's show creation function, called by self.load_live_shows.
        Parses the scraped HTML and adds ShowTuple named tuples to the
        object's self.shows list.
     
        :param str html: HTML scraped from the venue's concerts page.
        """

        summaries = self.get_summaries(html)

        for summary in summaries:

            artists = self.get_artist_billing(summary)
            venue_name, venue_id = self.get_venue_info(summary)
            show_date = self.get_show_date(summary)
            price = self.get_show_price(summary)
            show_url = self.get_show_url(summary)

            show_tup = Venue.show_fac(
                artists=artists, venue_name=venue_name,
                show_date=show_date, price=price,
                show_url=show_url, schedule_url=self.url,
            )

            self.shows.append(show_tup)


    def load_live_shows(self):
        """
        Scrapes the venue's concerts schedule page and populates
        self.shows list with ShowTuples if none exist yet.
        """

        if not self.shows:
            venue_html = requests.get(self.url)
            venue_html.raise_for_status()
            venue_html = venue_html.text
            self.make_shows(venue_html)
        else:
            print("This object seems to have shows already")