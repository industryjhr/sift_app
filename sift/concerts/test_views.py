# concerts/test_views.py
import datetime

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse

from .models import Artist, Concert, ConcertMatch, Venue
from .views import Home, UpcomingShows, ArtistsIndex, VenuesIndex, ConcertsIndex

class ViewsTest(TestCase):
    """
    Test 'em all.
    """

    def setUp(self):
        #self.factory = RequestFactory()

        ## TODO move to fixture
        # seed DB
        self.test_venue = Venue.objects.create(
            name='House of Bugs', address='123 Card St., Chicago, IL 60606',
            schedule_url='http://bugs.rock'
        )
        # bypass Artist.add_artist
        self.test_artist = Artist.objects.create(
            name='Toast Test', spotify_id='123spotify',
            re_string='\b\bToast.Test\b\b', is_active=True
        )
        self.test_concert = Concert.objects.create(pk=1,
            billing='Toast Test w/ The Toe Jam', venue=self.test_venue,
            date_time=datetime.datetime.utcnow(), price='Free.99',
            url='http://bugs.rock/TTwTTJ'
        )

        self.match = ConcertMatch.objects.create(concert=self.test_concert)
        self.test_concert.artists.add(self.test_artist)
        self.test_concert.save()
        self.match.artists.add(self.test_artist)
        self.match.save()

        # app URLs
        self.home_url = reverse('sift_home')
        self.upcoming_concerts_url = reverse('concerts:upcoming_shows')
        self.artist_index_url = reverse('concerts:artists')
        self.venue_index_url = reverse('concerts:venues')
        self.concert_index_url = reverse('concerts:all_concerts')

    def test_home(self):
        """
        Homepage should return a tagline.
        """

        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['tagline'])

    def test_upcoming_shows(self):
        """
        Check ConcertMatch objects returned.
        """

        response = self.client.get(self.upcoming_concerts_url)
        match_data = response.context['matches']
        self.assertEqual(len(match_data), 1)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(
            match_data[0].date_time,
            datetime.datetime(2010,1,1,tzinfo=datetime.timezone.utc)
        )

    def test_artists_index(self):
        #pass
        response = self.client.get(self.artist_index_url)
        self.assertEqual(response.status_code, 200)
        # accessing queryset response object from generic.ListView
        artist_data = response.context[0]['object_list']
        self.assertEqual(artist_data[0], self.test_artist)
        self.assertEqual(len(artist_data), 1)

    def test_venues_index(self):
        response = self.client.get(self.venue_index_url)
        self.assertEqual(response.status_code, 200)
        # accessing queryset response object from generic.ListView
        venue_data = response.context[0]['object_list']
        self.assertEqual(venue_data[0], self.test_venue)
        self.assertEqual(len(venue_data), 1)

    def test_venues_index(self):
        response = self.client.get(self.concert_index_url)
        self.assertEqual(response.status_code, 200)
        # accessing queryset response object from generic.ListView
        concert_data = response.context['concert_list']
        self.assertEqual(len(concert_data), 1)
        self.assertEqual(concert_data[0], self.test_concert)
        self.assertGreater(
            response.context['last_updated'],
            datetime.datetime(2010,1,1,tzinfo=datetime.timezone.utc)
        )