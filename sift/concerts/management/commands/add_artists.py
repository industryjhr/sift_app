"""
management/commands/add_artists.py

Add artist(s) to database.
"""
from datetime import datetime
import os, sys

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from concerts.models import Artist
from concerts.utils import FIXTURE_DIRS

class Command(BaseCommand):
    help = 'Add artists to the Artist table.'

    def add_arguments(self, parser):
        parser.add_argument('artists', nargs='+',
            help='Artist names to add, wrapped in double quotes if necessary')

    def handle(self, **options):
        
        # get manual confirmation that artists were entered correctly
        print("Artists to add:")
        for artist in options['artists']:
            self.stdout.write(artist)
        artists_verified = input("Continue? [y/n]: ")
        self.stdout.write("\n")
        if not artists_verified.lower() == 'y':
            sys.exit("\nAborting.\n")

        added_new_artists = False

        for artist_name in options['artists']:
            
            if Artist.objects.filter(name__iexact=artist_name).count():
                self.stdout.write("Existing artist {} found. Skipping..".format(
                    artist_name)
                )
                continue
            #except models.DoesNotExist: # desirable
            artist_obj = Artist.add_artist(artist_name)
            self.stdout.write("New Artist entry created: {}".format(artist_obj))
            added_new_artists = True

        if added_new_artists:
            # TODO fixture rotation?
            artist_fixture_name = datetime.utcnow().strftime('%Y%m%d') + '_artist.json'
            artist_fixture_path = os.path.join(FIXTURE_DIRS['artists'], artist_fixture_name)
            self.stdout.write("Dumping new Artist fixture: {}".format(artist_fixture_name))
            call_command(
                'dumpdata',
                'concerts.Artist',
                '--indent=4',
                '--output={}'.format(artist_fixture_path)
            )
            self.stdout.write("Done!\n")
        else:
            self.stdout.write("No new artists added.\n")