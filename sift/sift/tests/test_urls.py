# -*- coding: utf-8 -*-
# sift/tests/test_urls.py

from django.test import TestCase
from django.core.urlresolvers import resolve, reverse

class UrlsTest(TestCase):

    def setUp(self):

        # app URLs
        self.home_url = reverse('sift_home')

    def test_homepage_view_function_resolution(self):

        from concerts.views import Home # TODO move to core

        found = resolve(self.home_url)
        # TODO figure out why functions themselves are not equal
        self.assertEqual(found.func.__name__, Home.as_view().__name__)