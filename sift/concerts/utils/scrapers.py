"""
scrapers.py

Scraper objects for venues.
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
        t = time.strptime(html_time, '%I:%M %p')

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

        BL prices only available through TicketWeb (two 
        links and a search required).
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

class HouseOfBlues(Venue):
    """
    Scraper object for House of Blues (Chicago).

    329 N Dearborn St.
    Chicago, IL 60654
    """

    def __init__(self):
        super().__init__()
        self.venue_name = 'House of Blues'
        self.url = 'http://www.houseofblues.com/chicago'

    def load_live_shows(self):
        """
        Scrapes the venue's concerts schedule page and populates
        self.shows list with ShowTuples, if not self.shows.
        """

        if not self.shows:

            from selenium import webdriver
            driver = webdriver.PhantomJS()
            driver.set_window_size(1221, 686)
            driver.delete_all_cookies()
            driver.get(self.url)

            # set to list view
            list_xpath = '//*[@id="EventCalendar122"]/div[1]/div/section/div/div[3]/a[2]'
            list_button = driver.find_element_by_xpath(list_xpath)
            list_button.click()
            # play it safe, let page load
            time.sleep(4)
            venue_html = []
            venue_html.append(driver.page_source)

            next_month_xpath = '//*[@id="content"]/div[2]/div/section/header[2]/h2/a[2]/i'
            next_month_button = driver.find_element_by_xpath(next_month_xpath)

            for _ in range(2):
                # get next two months' shows as well                
                next_month_button.click()
                time.sleep(4)
                venue_html.append(driver.page_source)

            driver.quit()
            self.make_shows('\n'.join(venue_html))

        else:
            print("Shows list already populated")

    def get_summaries(self, html):
        """
        See Venue.get_summaries.

        html dump > '.c-calendar-list__item'
        And some page manipulation to get a couple months' worth of concerts.
        """

        all_summaries = bs(html, 'html.parser').select('.c-calendar-list__item')

        # "main" concerts at HoB will have 'Find Tickets Now' and
        # 'Event Details' buttons; filter everything else
        button_words = ['Find', 'Tickets', 'Now', 'Event', 'Details']
        concert_filter = \
            lambda summary: summary.select('.c-calendar-list__venue')[0].text.split() == button_words

        show_summaries = list(filter(concert_filter, all_summaries))

        return show_summaries

    def get_artist_billing(self, summary):
        """
        See Venue.get_artist_billing.

        summary > '.c-calendar-list__title'
        """

        return summary.select('.c-calendar-list__title')[0].text


    def get_venue_info(self, summary):
        """
        See Venue.get_venue_info.

        HoB concerts seem in-house only.
        """

        venue_name = self.venue_name
        venue_id = self.venue_id

        return (venue_name, venue_id)


    def get_show_date(self, summary):
        """
        See Venue.get_show_date.

        Date: summary > '.c-calendar-list__date-date'
        Time: summary > '.c-calendar-list__date-time'
        """
        
        # Dates on the site use abbreviations, conform to calendar.month_abbr.
        # Get month as number
        month_map = {k:v for v, k in enumerate(calendar.month_abbr)}

        concert_month_date = summary.select('.c-calendar-list__date-date')
        show_month, show_date = concert_month_date[0].text.strip(' ,\n').split()
        show_month = month_map[show_month.title()]

        if show_month >= TODAY.month:
            show_year = TODAY.year
        else:
            show_year = TODAY.year + 1

        show_time = summary.select('.c-calendar-list__date-time')[0].text.strip()
        show_time = time.strptime(show_time, '%I:%M%p')

        utc_datetime = Venue.make_utc_datetime(
            show_year=int(show_year),
            show_month=int(show_month),
            show_day=int(show_date),
            show_hour=show_time.tm_hour,
            show_minute=show_time.tm_min)

        return utc_datetime

    def get_show_price(self, summary):
        """
        See Venue.get_show_price.

        Ticket prices not directly on HoB site.
        """

        return 'Check ticket site for price.'

    def get_show_url(self, summary):
        """
        See Venue.get_show_url.

        '.btn-parent' > link from second item
        """

        details_button = summary.select('.btn-parent')[1]
        event_page = details_button.find('a', href=True)['href']

        return event_page

if __name__ == '__main__':
    main()