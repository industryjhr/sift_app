from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic

from .models import Artist, Concert, ConcertMatch, Venue

class Home(generic.View):
    """
    Return cover page.
    """

    def get(self, request):

        from random import choice

        taglines = (
            "Shake it 'til you bake it",
            "Whatever will bewilder me",
            "Properly following proper protocols",
            "Stopped to watch my emotions sway",
            "Reckon luck sees us the same",
            "The ocean floor is hidden from your viewing lens",
        )
        context = {'tagline': choice(taglines)}
        return render(request, 'concerts/sift_home.html', context)

class UpcomingShows(generic.View):
    """
    View list of concerts that have a tracked artist in their billing.
    """

    def get(self, request):
        """
        Return Concerts that have matched an artist in their billing,
        ordered by date ascending.
        """

        matched_concert_ids = list(ConcertMatch.objects.values_list('concert', flat=True))
        matches = Concert.objects.filter(id__in=matched_concert_ids).order_by('date_time')
        if Concert.objects.count():
            last_updated = Concert.objects.get(pk=1).date_scraped
        # TODO handle empty DB
        else:
            last_updated = datetime(1900,1,1)
        context = {
            'matches': matches,
            'last_updated': last_updated,
        }

        return render(request, 'concerts/upcoming_concerts.html', context)

class ArtistsIndex(generic.ListView):
    """
    View all artists being tracked.
    """
    queryset = Artist.objects.filter(is_active=True).order_by('name')

class VenuesIndex(generic.ListView):
    """
    View all venues being tracked.
    """
    queryset = Venue.objects.filter(is_active=True).order_by('name')

class ConcertsIndex(generic.View):
    """
    View all concerts in the DB, regardless of artist matches.
    """

    def get(self, request):
        """
        Return a list of all Concerts in the database.
        """
        concerts = Concert.objects.order_by('date_time')
        if concerts:
            last_updated = concerts[0].date_scraped
        # TODO handle empty DB
        else:
            last_updated = datetime(1900,1,1)
        context = {
            'concert_list': concerts,
            'last_updated': last_updated,
        }
        return render(request, 'concerts/concert_list.html', context)

if __name__=='__main__':
    pass
