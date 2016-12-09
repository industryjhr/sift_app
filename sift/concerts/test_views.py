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
        test_venue = Venue.objects.create(
            name='House of Bugs', address='123 Card St., Chicago, IL 60606',
            schedule_url='http://bugs.rock'
        )
        # bypass Artist.add_artist
        test_artist = Artist.objects.create(
            name='Toast Test', spotify_id='123spotify',
            re_string='\b\bToast.Test\b\b', is_active=True
        )
        test_concert = Concert.objects.create(pk=1,
            billing='Toast Test w/ The Toe Jam', venue=test_venue,
            date_time=datetime.datetime.utcnow(), price='Free.99',
            url='http://bugs.rock/TTwTTJ'
        )

        match = ConcertMatch.objects.create(concert=test_concert)
        test_concert.artists.add(test_artist)
        test_concert.save()
        match.artists.add(test_artist)
        match.save()

        # app URLs
        self.home_url = '' #?
        self.upcoming_concerts_url = reverse('concerts:upcoming_shows')

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
        self.assertEqual(len(response.context['matches']), 1)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(
            response.context['matches'][0].date_time,
            datetime.datetime(2010,1,1,tzinfo=datetime.timezone.utc)
        )