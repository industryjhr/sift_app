# -*- coding: utf-8 -*-
# concerts/scrapers/metro.py

from .venue import Venue

import calendar, datetime, iso8601, os, pytz, sys, time
from collections import namedtuple

import requests
from bs4 import BeautifulSoup as bs

TODAY = datetime.datetime.today()


class Metro(Venue):
    """
    Scraper object for Metro.
    
    3730 N. Clark St.
    Chicago, IL 60613
    http://metrochicago.com
    """

    def __init__(self):
        super().__init__()
        self.venue_name = 'Metro'
        self.url = 'http://metrochicago.com/shows/'


    def get_summaries(self, html):
        """
        See Venue.get_summaries.

        html dump > '.showContainer'
        """

        show_summaries = bs(html, 'html.parser').select('.showContainer')
        return show_summaries


    def get_artist_billing(self, summary):
        """
        See Venue.get_artist_billing.

        headliner: summary > '.headliner'
        supporting acts: summary > h3 > h3
        """

        headliner = summary.select('.headliner')[0].text.strip()

        supporting_artists = summary.select('h3 > h3')
        if supporting_artists:
            support_list = []

            for artist_element in supporting_artists:
                support_list.append(artist_element.text)
            support = ', '.join(support_list)

            return headliner + ' with ' + support

        return headliner

    def get_venue_info(self, summary):
        """
        See Venue.get_venue_info.

        Venue is external if summary > '.picCTA'.
        """

        if summary.select('.picCTA'):
            venue_name = summary.select('.picCTA')[0].text.strip()
            # sometimes "at external venue", sometimes just "external venue"
            if venue_name[:2].lower() == 'at':
                venue_name = venue_name[3:]
            venue_id = 99
        else:
            venue_name = self.venue_name
            venue_id = self.venue_id

        return (venue_name, venue_id)


    def get_show_date(self, summary):
        """
        See Venue.get_show_date.

        show date: summary > '.date' -> "Saturday, November 5"

        show time: summary > '.showinfo'
            -> "<ticket info> // <show time(s)> // <age info>"

        Use show time if multiple (eg. doors open vs. show time).
        """

        long_month, str_date = summary.select('.date')[0].text.strip().split()[1:]
        show_month = datetime.datetime.strptime(long_month, "%B").month

        if show_month >= TODAY.month:
            show_year = TODAY.year
        else:
            show_year = TODAY.year + 1

        # get show time
        show_info = summary.select('.showinfo')[0].text.strip()
        show_info_list = show_info.split('//')
        if len(show_info_list) == 1:
            # someone messed up and used single / instead of the predominant //
            # make the show time string the second element in show_info_list
            show_info_list = show_info.split('/')
            show_info_list = ['placeholder text', show_info_list[1] + '/' + show_info_list[2]]

        show_times = show_info_list[1].strip()
        if len(show_times.split('/')) > 1:
            # "Doors: <time> / Show: <time>"" in that order; use show time
            show_time = show_times.split('/')[1].strip().split()[1]
        else:
            show_time = show_times

        # time range, eg. 9PM - 5AM
        # take first for start of concert
        if show_time.count('-'):
            show_time = show_time.split('-')[0].strip()

        if show_time.count(':'):
            # eg. '7:30PM'
            t = time.strptime(show_time, '%I:%M%p')
        else:
            # eg. '7PM'
            t = time.strptime(show_time, '%I%p')

        utc_datetime = Venue.make_utc_datetime(
            show_year=int(show_year),
            show_month=int(show_month),
            show_day=int(str_date),
            show_hour=t.tm_hour,
            show_minute=t.tm_min
        )

        return utc_datetime


    def get_show_price(self, summary):
        """
        See Venue.get_show_price.

        summary > '.showinfo'
            -> "<ticket info> // <show time(s)> // <age info>"
        """

        show_info = summary.select('.showinfo')[0].text.strip()
        show_info_list = show_info.split('//')
        if len(show_info_list) == 1:
            # someone messed up and used single /s instead of the predominant //s
            price_string = show_info.split('/')[0].strip()
        else:
            price_string = show_info_list[0].strip()

        return price_string


    def get_show_url(self, summary):
        """
        See Venue.get_show_url.

        summary > first link
        """

        show_url = summary.find('a', href=True)['href']
        return show_url