# -*- coding: utf-8 -*-
"""
concerts/scrapers/lh-st.py

Parent scraper class for both Lincoln Hall and Schubas Tavern, as they
share a homepage (www.lh-st.com).

The scraping functions should generally be the same, but the subclasses will
define which venue is selected by selenium.
"""

import calendar, datetime, iso8601, os, pytz, sys, time
from collections import namedtuple

import requests
from bs4 import BeautifulSoup as bs

from .venue import Venue

TODAY = datetime.datetime.today()

class LHSTParent(Venue):
    """
    Scraper object for Lincoln Hall and Schubas Tavern.

    The venues share a website, and so the scraping particulars can be defined
    here mostly, with the subclasses overriding load_live_shows to select
    their particular venue via selenium.

    http://www.lh-st.com/
    """

    def __init__(self):
        super().__init__()
        #self.venue_name // defined in subclass
        #self.VENUE_CLASS_NAME // defined in subclass
        self.url = 'http://www.lh-st.com'


    def _build_html_blob(self):
        """
        For sites that display one month at a time.
        Returns a concatenated blob of html for some number of months. 
        """

        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        CURRENT_MONTH_XPATH = '//*[@id="monthFilter"]/a[2]'
        NEXT_MONTH_XPATH = '//*[@id="monthFilter"]/a[3]'
        NEXT_NEXT_MONTH_XPATH = '//*[@id="monthFilter"]/a[4]'

        driver = webdriver.PhantomJS()
        driver.set_window_size(1221, 686)
        driver.delete_all_cookies()
        driver.get(self.url)


        # http://docs.seleniumhq.org/docs/04_webdriver_advanced.jsp#explicit-and-implicit-waits
        def _wait_function():
            time.sleep(3)
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "showItem")))

        def _pick_out_venue_shows(html_blob):
            """
            Pick out either the Lincoln Hall or Schubas shows from the blob.
            This is all to get around the failure to filter by Selenium.
            """

            soup = bs(html_blob, 'html.parser')
            shows = soup.select(self.VENUE_CLASS_NAME)
            shows_html = '\n'.join((show.__str__() for show in shows))
            return shows_html


        venue_html_list = []
        current_month_button = driver.find_element_by_xpath(CURRENT_MONTH_XPATH)
        next_month_button = driver.find_element_by_xpath(NEXT_MONTH_XPATH)
        next_next_month_button = driver.find_element_by_xpath(NEXT_NEXT_MONTH_XPATH)
        month_buttons = (current_month_button, next_month_button, next_next_month_button)

        # three months of shows
        try:
            for button in month_buttons:
                button.click()
                _wait_function()
                shows_html = _pick_out_venue_shows(driver.page_source)
                venue_html_list.append(shows_html)
        finally:
            driver.quit()

        return('\n'.join(venue_html_list))


    def load_live_shows(self):
        """
        Scrapes the venue's concerts schedule page and populates
        self.shows list with ShowTuples, if not self.shows.
        """

        if not self.shows:
            html_blob = self._build_html_blob()
            self.make_shows(html_blob)
        else:
            print("Shows list already populated")


    def get_summaries(self, html):
        """
        See Venue.get_summaries.

        html dump > '.showItem'
        And some page manipulation to get a couple months' worth of concerts.
        """

        show_summaries = bs(html, 'html.parser').select('.showItem')
        return show_summaries


    def get_artist_billing(self, summary):
        """
        See Venue.get_artist_billing.

        summary > '.bands'
        """

        return summary.select('.bands')[0].text.strip().replace('\n', ', ')


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

        Date: summary > '.header'
        Time: summary > '.ticketInfo'
        """

        # Dates on the site use abbreviations, conform to calendar.month_abbr.
        # Get month as number
        month_map = {k:v for v, k in enumerate(calendar.month_abbr)}

        # year and month run together with no delimiter :/
        date_string = summary.select('.header')[0].text.strip()[-11:]
        month_abbr, show_date, show_year = date_string.split()
        show_month = month_map[month_abbr.title()]

        time_info = summary.select('.ticketInfo')[0].text.strip().replace('\n', ' ')
        time_info = time_info.split()
        # time info location is unpredictable
        try:
            period_index = time_info.index('PM')
        except ValueError:
            period_index = time_info.index('AM')
        show_time = time_info[period_index-1] + time_info[period_index]
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

        summary > '.avail'
        """

        return summary.select('.avail')[0].text.strip().split()[0]


    def get_show_url(self, summary):
        """
        See Venue.get_show_url.

        summary > '.ecomm' > link
        """

        link_div = summary.select('.buttons')[0]
        try:
            event_uri = link_div.find('a', href=True)['href']
        except TypeError:
            # XXX actually handle
            event_uri = ''

        return self.url + event_uri
