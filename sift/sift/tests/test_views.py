# -*- coding: utf-8 -*-
# sift/tests/test_views.py

from django.test import TestCase
from django.core.urlresolvers import resolve, reverse

class UrlsTest(TestCase):

    def setUp(self):

        # app URLs
        self.home_url = reverse('sift_home')

    def test_homepage_returns_correct_html(self):

        response = self.client.get(self.home_url)
        html = response.content.decode('utf8')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(html.startswith('<!DOCTYPE html>'))
        self.assertIn('Ravesloot', html)
        self.assertTrue(html.endswith('</html>'))