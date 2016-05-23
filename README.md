# sift(.herokuapp.com)
#### a WIP django site to check local (Chicago) concert venues for shows played by particular artists


<i>about importing artists from itunes</i>

iTunes provides the option to dump basically everything about its library to xml.  
Using the python standard lib parser (xml.etree.cElementTree), it's not <i>too</i> difficult to pull anything out once you understand the structure.

To get the artists, I did something like this:

<tt>
parsley = xml.etree.cElementTree.XML(xml_string)

# have to drill down and run through individual tracks
tracks_xml = parsley[0][15]

artists = set()

# odd items in tracks_xml are individual songs; song[5] is the artist element
for track in tracks_xml:
    try:
        artists.add(track[5].text)
    except IndexError:
        continue
</tt>

Depending on the state of your library, you may have to clean up the list a bit, optionally removing undesirable/inactive artists.
