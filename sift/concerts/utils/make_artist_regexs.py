"""
concerts/utils/make_artist_regexs.py

TODO move to management command?

Iterate through the artists fixture json and save a regex of of the artist
name to a fixture file, to later become artist.re_string on the
concerts.models.Artist objects.

Called with two posargs: <fixture_input.json> <output_filename.json>
"""

import json, os, re, string, sys

PUNC_RE = re.compile(
    '[{}]'.format(string.punctuation),
    flags=re.I|re.M|re.DOTALL
)

try:
    fixture_filename = sys.argv[1]
    write_file = sys.argv[2]
except IndexError:
    sys.exit(
        "Called with two posargs: <fixture_input.json> <output_filename.json>"
    )

try:
    with open(fixture_filename) as fhand:
        artists_json = json.load(fhand)
except FileNotFoundError:
    sys.exit("File {} not found".format(fixture_filename))

for entry in artists_json:

    display = entry['fields']['name']
    no_punc = re.sub(PUNC_RE, r'.?', display)
    no_end = re.sub(r'$', '\\\\b', no_punc)
    cleaned = re.sub(r'^', '\\\\b', no_end)
    entry['fields']['re_string'] = cleaned

with open(write_file, 'w') as fhand:
    json.dump(artists_json, fhand, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
