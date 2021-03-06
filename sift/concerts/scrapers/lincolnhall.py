# -*- coding: utf-8 -*-
"""
concerts/scrapers/lincolnhall.py

Scraper class for Lincoln Hall, inheriting from the Lincoln Hall - Schubas
Tavern shared parent, as they share a homepage (www.lh-st.com).

The scraping functions should generally be the same, but the subclasses will
define which venue is selected by selenium (via VENUE_XPATH).
"""

from .lh_st import LHSTParent

class LincolnHall(LHSTParent):
    """
    Scraper object for Lincoln Hall.

    The venues share a website, and so the scraping particulars can be defined
    here mostly, with the subclasses overriding load_live_shows to select
    their particular venue via selenium.

    http://www.lh-st.com/
    """

    def __init__(self):
        super().__init__()
        self.venue_name = 'Lincoln Hall'
        self.url = 'http://www.lh-st.com'
        self.VENUE_CLASS_NAME = '.LincolnHall'