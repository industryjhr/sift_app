import calendar, datetime, iso8601, os, pytz, sys, time
from collections import namedtuple

import requests
from bs4 import BeautifulSoup as bs

from .venue import Venue

TODAY = datetime.datetime.today()

class HouseOfBlues(Venue):
    """
    Scraper object for House of Blues (Chicago).

    329 N Dearborn St.
    Chicago, IL 60654
    http://houseofblues.com/chicago/
    """

    def __init__(self):
        super().__init__()
        self.venue_name = 'House of Blues'
        self.url = 'http://houseofblues.com/chicago'

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

            next_month_xpath = '//*[@id="content"]/div[2]/div/section/header[1]/h2/a[2]/i'
            #next_month_xpath = '//*[@id="content"]/div[2]/div/section/header[2]/h2/a[2]/i'
            next_month_button = driver.find_element_by_xpath(next_month_xpath)

            # get next two months' shows as well
            for _ in range(2):
                # reset to list view
                list_button.click()
                time.sleep(4)
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