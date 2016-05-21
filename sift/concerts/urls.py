from django.conf.urls import url

from . import views

app_name = 'concerts'
urlpatterns = [
    url(r'^$', views.UpcomingShows.as_view(), name='upcoming_shows'),
    url(r'^artists/$', views.ArtistsIndex.as_view(), name='artists'),
    url(r'^venues/$', views.VenuesIndex.as_view(), name='venues'),
    url(r'^all/$', views.ConcertsIndex.as_view(), name='concerts'),
]
