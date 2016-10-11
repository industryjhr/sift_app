"""
concerts/utils/scraper_reference.py

Dictionary lookup for venue scraper objects, where the key
is the concerts.models.Venue object's pk, value is scraper object.

Used by the concerts.scrape_shows management command.
"""

from concerts.utils import scrapers

SCRAPERS = {
    1: scrapers.EmptyBottle,
    2: scrapers.BottomLounge,
    3: scrapers.Subterranean,
    4: scrapers.DoubleDoor,
    5: scrapers.HouseOfBlues,
}

if __name__ == '__main__':
	pass