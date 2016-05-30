from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic

from .models import Artist, Concert, ConcertMatch, Venue

class Home(generic.View):

    def get(self, request):
        return render(request, 'concerts/sift_home.html')

class UpcomingShows(generic.View):

    def get(self, request):
        matched_concert_ids = list(ConcertMatch.objects.values_list('concert', flat=True))
        matches = Concert.objects.filter(id__in=matched_concert_ids)
        last_updated = Concert.objects.get(pk=1).date_scraped
        context = {
            'matches': matches,
            'last_updated': last_updated,
        }

        return render(request, 'concerts/upcoming_concerts.html', context)


class ArtistsIndex(generic.ListView):
    queryset = Artist.objects.filter(is_active=True).order_by('name')


class VenuesIndex(generic.ListView):
    queryset = Venue.objects.filter(is_active=True).order_by('name')

class ConcertsIndex(generic.View):

    def get(self, request):
        concerts = Concert.objects.all()
        last_updated = Concert.objects.get(pk=1).date_scraped
        context = {
            'concert_list': concerts,
            'last_updated': last_updated,
        }
        return render(request, 'concerts/concert_list.html', context)
