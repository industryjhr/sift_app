Concerts Management Commands
============================

.. _refresh_heroku:

refresh_heroku
--------------

:code:`./manage.py refresh_heroku`

Management command to refresh data on Heroku deployment.

Flushes and re-seeds the DB from Artist, Venue, and Concert fixtures,
then runs the make_matches management commmand to populate ConcertMatch table.

This workflow is currently necessary due to being unable to scrape the
Subterranean site from Heroku's servers. cf. concerts/buffering_error.txt.


.. _refresh_dev:

refresh_dev
-----------

:code:`./manage.py refresh_dev`

Management command to refresh data on dev deployment.

Flushes the DB and re-seeds Artist and Venue from fixtures, then
runs scrape_shows and make_matches commmands to populate ConcertMatch table.

Also dumps Concerts to a fixture for the Heroku app to use.


.. _get_spotify_artist_ids:

get_spotify_artist_ids
----------------------

:code:`./manage.py get_spotify_artist_ids`

For Artist entires without a spotify_id, queries the Spotify API for
artist ID and saves it to the DB.


.. _scrape_shows:

scrape_shows
------------

:code:`./manage.py scrape_shows`

Using the concerts.utils.scrapers, scrapes venue sites and
writes the upcoming concerts to Concerts table.

While this can be run on its own, this serves as a part of the
refresh_* management commands.

.. _make_matches:

make_matches
------------

Uses the Artist.re_string to search for the artist in the
concert lineup (Concert.billing) of each concert.  If a match is found,
saves a ConcertMatch object for lookup later.

While this can be run on its own, this serves as a part of the
refresh_* management commands.
