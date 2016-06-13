"""
scrapers.py

Scraper objects for venues

scraper field on venue model objects key to lookup here(?)
"""

import calendar, datetime, os, sys, time
from collections import namedtuple

from bs4 import BeautifulSoup as bs
import iso8601
import pytz
import requests

TODAY = datetime.datetime.today()


ShowTuple = namedtuple(
                'show',
                'artists, venue_name, show_date, price, show_url, schedule_url'
            )


class Venue:
    """Base class for venue scrapers"""

    show_fac = ShowTuple
    # TODO remove venue_id logic, now tracked in models

    def __init__(self, **kwargs):
        self.shows = []
        self.venue_id = 99

    def __str__(self):
        return "{0} -- {1} current shows".format(self.venue_name, len(self.shows))


    def get_summaries(self, html):
        """Returns list of parent beautifulsoup elements for shows."""
        raise NotImplementedError("get_summaries is venue-specific")


    def get_artist_billing(self, summary):
        """Pulls artist information for the show."""
        raise NotImplementedError("get_artist_bililng is venue-specific")


    def get_venue_info(self, summary):
        """Return venue name and id for the show."""
        raise NotImplementedError("get_venue_info is venue-specific")


    def get_show_date(self, summary):
        """Returns UTC datetime object from show summary HTML"""
        raise NotImplementedError("get_show_date is venue-specific")

    @staticmethod
    def make_utc_datetime(*args, **kwargs):
        """Converts naive (local; time as scraped) datetime object to UTC"""

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
        """Return price (as string) for the show."""
        raise NotImplementedError("get_show_price is venue-specific")


    def get_show_url(self, summary):
        """Return url for the show's details page."""
        raise NotImplementedError("get_show_price is venue-specific")


    def make_shows(self, html):
        """
        Uses the venue's scraped schedule HTML as input and
        populates the scraper object's shows list with ShowTuples.

        A 'summary' here is a slice of HTML that contains
        all known information about a single concert.
        Ie. all relevant information about a show is present in its summary.
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
        """Scrapes venue site and populates self.shows list with ShowTuples."""

        if not self.shows:
            venue_html = requests.get(self.url)
            venue_html.raise_for_status()
            venue_html = venue_html.text
            self.make_shows(venue_html)
        else:
            print("This object seems to have shows already")

    """
    def filter_shows(self):
        self.shows = self.writer.filter_new(self.shows)
    """

class BottomLounge(Venue):
    """Scraper object for Bottom Lounge"""

    def __init__(self):
        super().__init__()
        self.venue_name = 'Bottom Lounge'
        self.url = 'http://bottomlounge.com/events'


    def get_summaries(self, html):
        """Returns list of parent bs elements for shows """

        show_summaries = bs(html, 'html.parser').select('.schedule-item-content')
        return show_summaries


    def get_artist_billing(self, summary):
        """Pulls artist billing for a specific show"""

        # artist billing as one string; could break down on ' * '
        artists = summary.select('.schedule-title')[0].text

        return artists


    def get_venue_info(self, summary):
        """
        Some venues promote shows at other venues.
        In such cases, use venue_id 99 for misc. venues.
        """

        # BL seems to promote in-house shows only
        venue_name = self.venue_name
        # TODO remove venue_id logic
        venue_id = 99

        return (venue_name, venue_id)


    def get_show_date(self, summary):
        """TODO"""

        dt_spans = summary.select('.schedule-date')[0].find_all('span')
        show_month, show_date, show_year = tuple(dt_spans[0].text.split('/'))

        html_time = ' '.join(dt_spans[1].text.split()[-2:])
        # XXX *one* show on the site right now doesn't have AM/PM: 'Show 6:00'
        # in such cases, going to assume it's PM; might want to handle earlier?
        if html_time.split()[0].isalpha():
            html_time = '{} PM'.format(html_time.split()[1])

        # convert str to 24hr
        t = time.strptime(html_time, '%I:%M %p')

        utc_datetime = Venue.make_utc_datetime(
            show_year=int(show_year),
            show_month=int(show_month),
            show_day=int(show_date),
            show_hour=t.tm_hour,
            show_minute=t.tm_min)

        return utc_datetime


    def get_show_price(self, summary):
        """Pulls price string for a specific show"""

        # BL prices only available through TicketWeb.. pull all from TW???
        price = 'NOT ON SITE'
        return price


    def get_show_url(self, summary):
        """Pulls url for a specific show"""

        show_url = summary.find('a', href=True)['href']
        return show_url


# TODO move to docs
"""
Parsing notes

shows in <div class="schedule-item-content">
soupy.select('.schedule-item-content')

date and time in <div class="schedule-date">  >  spans
dt_obj = show.select('.schedule-date')
spans = dt_obj[0].find_all('span')
date = spans[0]
time = spans[1] # doors time and show time; use show time
"""


class EmptyBottle(Venue):
    """Scraper object for The Empty Bottle"""

    def __init__(self):
        super().__init__()
        self.venue_name = 'The Empty Bottle'
        self.url = 'http://emptybottle.com'
        # EB dates conform to calendar.month_abbr
        self.month_map = {k:v for v, k in enumerate(calendar.month_abbr)}

    def get_summaries(self, html):
        """Returns list of parent bs elements for shows """

        show_summaries = bs(html, 'html.parser').select('.show_summary')
        return show_summaries


    def get_artist_billing(self, summary):
        """Pulls artist billing for a specific show"""

        # artist billing as one string; could break down on ' \n '
        artists = \
            summary.select('.show_artists')[0].text.replace('\n', '')
        return artists


    def get_venue_info(self, summary):
        """Pull venue for a show; some produced by EB but hosted elsewhere.
           In such cases, use venue_id 99 for misc. venues
           Returns tuple (<venue_name>, <venue_id>) """

        if summary.select('.show_venue'):
            venue_name = summary.select('.show_venue')[0].text.strip()
            venue_id = 99
        else:
            venue_name = self.venue_name
            venue_id = self.venue_id

        return (venue_name, venue_id)


    def get_show_date(self, summary):
        """Returns UTC datetime object for concert date and time"""

        # TODO instantiate once, higher up; currently for each show
        today = datetime.datetime.today()

        date_on_site = summary.select('.tw-event-date')[0].text
        # month as number (1-12)
        show_month = self.month_map[date_on_site.split()[0]]
        show_date = int(date_on_site.split()[1])
        if show_month >= today.month:
            show_year = today.year
        else:
            show_year = today.year + 1

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
        """Pulls price string for a specific show"""

        price = summary.select('.show_price')[0].text.strip()
        return price


    def get_show_url(self, summary):

        show_url = summary.find('a', href=True)['href']
        return show_url


# TODO move to docs
"""
Parsing info

html.select('.show_summary') # individual shows
div .show_summary > a .show_link # eg. "http://emptybottle.com/show/#######" >
span .show_details

> span .show_artists # artists billing > ul > li > artist string (individual)

> span .show_date # DoW, Date, Time >
.show_date > .tw-day-of-week # DoW, abbrev. eg. "Fri"
.show_date > .tw-event-date-complete > .tw-event-date # date, eg. "Jan 08"
.show_date > .tw-even-time-complete > .tw-event-time # time, eg. "5:30 pm"

> span .show_price # eg. "$10.00"

> span .show_venue # if span exists, show is at another venue

"""

class Subterranean(Venue):
    """Scraper object for Subterranean"""

    def __init__(self):
        super().__init__()
        self.venue_name = 'Subterranean'
        self.url = 'http://www.subt.net'

    def get_summaries(self, html):
        """Returns list of parent bs elements for shows """

        show_summaries = bs(html, 'html.parser').select('.list-view-item')
        return show_summaries

    def get_artist_billing(self, summary):
        """Pulls artist billing for a specific show"""

        # headlining and support acts in separate tags; supporting acts optional
        headliners = summary.select('.list-view-details > .headliners')[0].text
        try:
            support = summary.select('.list-view-details > .supports')[0].text
        except IndexError:
            return headliners

        return headliners + ' with ' + support


    def get_venue_info(self, summary):
        """
        Some venues promote shows at other venues.
        In such cases, use venue_id 99 for misc. venues (or check db?)
        """

        venue_name = self.venue_name
        venue_id = self.venue_id

        return (venue_name, venue_id)


    def get_show_date(self, summary):
        """Create UTC datetime object for concert date, time"""

        show_iso = summary.select('.value-title')[0].attrs['title']
        local_datetime = iso8601.parse_date(show_iso)
        return local_datetime.astimezone(pytz.utc)

    def get_show_price(self, summary):
        """Return price as a string from a concert summary"""

        try:
            price = summary.select('.price-range')[0].text.strip()
        except IndexError:
            price = 'No price / free?'
        return price

    def get_show_url(self, summary):
        """Returns url to a concert page from a summary"""

        show_page = summary.find('a', href=True)['href']
        # show_page link relative
        return self.url + show_page


"""
Parsing notes



"""
