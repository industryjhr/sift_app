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
        #context = {'concerts': []}
        matches = Concert.objects.filter(id__in=matched_concert_ids)

        #context_object_name = 'concerts'
        return render(request, 'concerts/concertmatch_list.html', {'matches': matches})


class ArtistsIndex(generic.ListView):
    queryset = Artist.objects.filter(is_active=True).order_by('name')


class VenuesIndex(generic.ListView):
    queryset = Venue.objects.filter(is_active=True).order_by('name')

class ConcertsIndex(generic.ListView):
    model = Concert
