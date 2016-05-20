from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic

from .models import Artist, Concert, ConcertMatch, Venue

# Create your views here.

"""
def upcoming(request):
    return HttpResponse("Upcoming schedule displayed here")
"""

class UpcomingShows(generic.View):

    def get(self, request):
        matched_concert_ids = list(ConcertMatch.objects.values_list('concert', flat=True))
        #context = {'concerts': []}
        matches = Concert.objects.filter(id__in=matched_concert_ids)

        #context_object_name = 'concerts'
        return render(request, 'shows/concertmatch_list.html', {'matches': matches})


class ArtistsIndex(generic.ListView):
    queryset = Artist.objects.order_by('name')


class VenuesIndex(generic.ListView):
    model = Venue
