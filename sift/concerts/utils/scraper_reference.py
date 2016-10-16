"""
concerts/utils/scraper_reference.py

Dictionary lookup for venue scraper objects, where the key
is the concerts.models.Venue object's pk, value is scraper object.

Used by the concerts.scrape_shows management command.
"""

from .scrapers import (
    emptybottle,
    bottomlounge,
    subterranean,
    doubledoor,
    houseofblues,
)

SCRAPERS = {
    1: emptybottle.EmptyBottle,
    2: bottomlounge.BottomLounge,
    3: subterranean.Subterranean,
    4: doubledoor.DoubleDoor,
    5: houseofblues.HouseOfBlues,
}

if __name__ == '__main__':
	pass