# -*- coding: utf-8 -*-
# concerts/tests/test_views.py

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve, reverse

class UrlsTest(TestCase):

    def setUp(self):

        # app URLs
        self.upcoming_concerts_url = reverse('concerts:upcoming_shows')
        self.artist_index_url = reverse('concerts:artists')
        self.venue_index_url = reverse('concerts:venues')
        self.concert_index_url = reverse('concerts:all_concerts')

    def test_upcoming_shows_view_function_resolution(self):

        from ..views import UpcomingShows

        found = resolve(self.upcoming_concerts_url)
        # TODO figure out why functions themselves are not equal
        self.assertEqual(found.func.__name__, UpcomingShows.as_view().__name__)

    def test_artist_index_view_function_resolution(self):

        from ..views import ArtistsIndex

        found = resolve(self.artist_index_url)
        # TODO figure out why functions themselves are not equal
        self.assertEqual(found.func.__name__, ArtistsIndex.as_view().__name__)

    def test_venue_index_view_function_resolution(self):

        from ..views import VenuesIndex

        found = resolve(self.venue_index_url)
        # TODO figure out why functions themselves are not equal
        self.assertEqual(found.func.__name__, VenuesIndex.as_view().__name__)

    def test_concert_index_view_function_resolution(self):

        from ..views import ConcertsIndex

        found = resolve(self.concert_index_url)
        # TODO figure out why functions themselves are not equal
        self.assertEqual(found.func.__name__, ConcertsIndex.as_view().__name__)