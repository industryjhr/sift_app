# sift(.herokuapp.com)
#### A WIP Django site to check local (Chicago) concert venues for shows played by particular artists.

Artists were pulled from an XML dump of an iTunes library.

Web scrapers (concerts/scrapers.py) for local venues are used to populate a Concerts table.  The concerts' artist billings are then searched for the tracked artists, and matches are saved.  The search is fairly permissive and errs on the side of too many matches currently.  Still better than scrolling through dozens of event emails!

The site is currently hosted on Heroku at http://sift.herokuapp.com
