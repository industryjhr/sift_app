# -*- coding: utf-8 -*-
# concerts/scrapers/doubledoor.py

import calendar, datetime, iso8601, os, pytz, sys, time
from collections import namedtuple

import requests
from bs4 import BeautifulSoup as bs

from .venue import Venue

TODAY = datetime.datetime.today()

class DoubleDoor(Venue):
    """
    Scraper object for Double Door.
    
    1551 N. Damen Ave.
    Chicago, IL, 60622
    http://doubledoor.com
    """

    def __init__(self):
        super().__init__()
        self.venue_name = 'Double Door'
        self.url = 'http://doubledoor.com'

    def load_live_shows(self):
        """
        Scrapes the venue's concerts schedule page and populates
        self.shows list with ShowTuples, if not self.shows.
        """

        if not self.shows:
            # thanks, obama
            user_agent = ("Mozilla/5.0 (Windows NT 6.3; rv:36.0) "
                          "Gecko/20100101 Firefox/36.0"
            )
            headers = {'user-agent': user_agent}

            venue_html = requests.get(self.url, headers=headers)
            venue_html.raise_for_status()
            venue_html = venue_html.text
            self.make_shows(venue_html)
        else:
            print("Shows list already populated")


    def get_summaries(self, html):
        """
        See Venue.get_summaries.

        html dump > '.rhino-event-wrapper'
        """

        show_summaries = bs(html, 'html.parser').select('.rhino-event-wrapper')
        return show_summaries


    def get_artist_billing(self, summary):
        """
        See Venue.get_artist_billing.

        '.rhino-event-wrapper' >
            '.rhino-event-header' (Headliner)
            '.rhino-event-subheader' (Support)
        """

        # artist billing as one string; could break down on ' * '
        headliner = summary.select('.rhino-event-header')[0].text.strip()
        try:
            support = summary.select('.rhino-event-subheader')[0].text.strip()
        except IndexError:
            support = ''
        # "So And Sos with Supporting Acks * Sep'd by Asterisks"
        return headliner + ' ' + support


    def get_venue_info(self, summary):
        """
        See Venue.get_venue_info.

        Double Door appears currently to promote in-house shows only.
        """

        # BL seems to promote in-house shows only
        venue_name = self.venue_name
        # TODO remove venue_id logic
        venue_id = 99

        return (venue_name, venue_id)


    def get_show_date(self, summary):
        """
        See Venue.get_show_date.

        '.rhino-event-wrapper' > 
            '.rhino-event-datebox-month' (month, abbrev. eg. 'Sep')
            '.rhino-event-datebox-date' (date)
            '.rhino-event-time' (time, eg. '7:00 PM')
        """

        # Months on DD abbreviated, conform to calendar.month_abbr
        month_map = {k:v for v, k in enumerate(calendar.month_abbr)}

        show_month = summary.select('.rhino-event-datebox-month')[0].text.strip()
        show_month = month_map[show_month]

        if show_month >= TODAY.month:
            show_year = TODAY.year
        else:
            show_year = TODAY.year + 1

        show_date = summary.select('.rhino-event-datebox-date')[0].text.strip()

        html_time = summary.select('.rhino-event-time')[0].text
        time_24_hr = time.strptime(html_time, '%I:%M %p')

        utc_datetime = Venue.make_utc_datetime(
            show_year=int(show_year),
            show_month=int(show_month),
            show_day=int(show_date),
            show_hour=time_24_hr.tm_hour,
            show_minute=time_24_hr.tm_min
        )

        return utc_datetime


    def get_show_price(self, summary):
        """
        See Venue.get_show_price.

        '.rhino-event-wrapper' > '.rhino-event-price'
        """

        price = summary.select('.rhino-event-price')[0].text.strip()
        return price


    def get_show_url(self, summary):
        """
        See Venue.get_show_url.

        '.rhino-event-wrapper' > first link
        """

        show_url = summary.find('a', href=True)['href']
        return show_url