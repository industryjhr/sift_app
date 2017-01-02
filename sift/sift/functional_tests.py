# -*- coding: utf-8 -*-
# sift/functional_tests.py

import unittest

from selenium import webdriver

class HomepageTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.PhantomJS()

    def test_homepage_loads(self):
        self.browser.get('http://localhost:8000')
        self.assertIn('sift', self.browser.title)

if __name__=='__main__':

    unittest.main()

    # click 'Concerts' to get to /concerts/ ('Upcoming Concerts')

    # click 'Artists' to get to /concerts/artists/ ('Artists tracked')

    # click 'Venues' to get to /concerts/venues/ ('Venues tracked')

    # click 'All Shows' to get to /concerts/all/ ('All concerts')
