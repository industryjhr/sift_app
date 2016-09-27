# sift(.herokuapp.com)
#### A Django project to check local (Chicago) concert venues for shows played by particular artists.

The majority of the tracked artists were pulled from an XML dump of an iTunes library.

I periodically scrape local venue sites and dump concert listings to the database, after which the artist billings for the shows are searched for the tracked artists.  Matches are saved and displayed at sift.herokuapp.com/concerts/, along with some additional info (link to the artist on Spotify).

The site is currently hosted on Heroku at https://sift.herokuapp.com.
