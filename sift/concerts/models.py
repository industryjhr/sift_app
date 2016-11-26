from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    re_string = models.CharField(max_length=200)
    spotify_id = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    schedule_url = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Concert(models.Model):
    billing = models.CharField(max_length=400)
    artists = models.ManyToManyField(Artist)
    venue = models.ForeignKey(
        Venue,
        on_delete = models.SET_NULL,
        blank = True,
        null = True,
    )
    date_time = models.DateTimeField()
    price = models.CharField(max_length=100)
    url = models.CharField(max_length=300)
    date_scraped = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{0} - {1} at {2}".format(
            self.date_time.strftime('%m.%d'),
            self.billing,
            self.venue,
        )

class ConcertMatch(models.Model):
    artists = models.ManyToManyField(Artist)
    concert = models.OneToOneField(
        Concert,
        on_delete = models.CASCADE,
    )
