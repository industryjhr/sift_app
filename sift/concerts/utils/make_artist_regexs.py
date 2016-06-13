import json, os, re, string, sys

"""
make_artist_regexs.py

Iterates through the artists fixture json to update artist regexs
"""

#CATCH_ALL = '.*?'
CATCH_ALL = '\b'
COMMON_WORDS = ['the', 'and', 'of']
# beginning and end of line? raw string MAGIC?
#THE_RE = re.compile(r'\bTHE\b', flags=re.IGNORECASE|re.MULTILINE|re.DOTALL)
#AND_RE = re.compile(r'\bAND\b', flags=re.IGNORECASE|re.MULTILINE|re.DOTALL)
#OF_RE = re.compile(r'\bOF\b', flags=re.IGNORECASE|re.MULTILINE|re.DOTALL)

#PUNC_WHITESPACE_RE = re.compile('[{}]+'.format(string.punctuation + string.whitespace), flags=re.I|re.M|re.DOTALL)

#PUNC_WHITESPACE_RE = re.compile(r'[\s\W]', flags=re.I|re.M|re.DOTALL)

PUNC_RE = re.compile('[{}]'.format(string.punctuation), flags=re.I|re.M|re.DOTALL)
WHITESPACE_RE = re.compile(r'\s', flags=re.I|re.M|re.DOTALL)

try:
    fixture_filename = sys.argv[1]
    write_file = sys.argv[2]
except IndexError:
    sys.exit("Please call with two posargs: <fixture_input.json> <output_filename.json>")

try:
    with open(fixture_filename) as fhand:
        artists_json = json.load(fhand)
except FileNotFoundError:
    sys.exit("File {} not found".format(fixture_filename))


for entry in artists_json:

    display = entry['fields']['name']
    """
    no_the  = re.sub(THE_RE, ' ', display)
    no_and  = re.sub(AND_RE, ' ', no_the)
    no_of   = re.sub(OF_RE, ' ', no_and)
    """
    no_punc = re.sub(PUNC_RE, r'.?', display)
    #no_whitespace = re.sub(WHITESPACE_RE, r'[.]?', no_punc)
    no_beginning = re.sub(r'$', '\\b', no_punc)
    cleaned = re.sub(r'^', '\\b', no_beginning)

    #cleaned = re.sub(PUNC_WHITESPACE_RE, CATCH_ALL, display)
    entry['fields']['re_string'] = cleaned

with open(write_file, 'w') as fhand:
    json.dump(artists_json, fhand, indent=4, ensure_ascii=False)

"""
re.sub(PUNC_WHITESPACE_RE, CATCH_ALL, target_string, flags=re.I|re.M|re.DOTALL) 

artist_re = re.compile({}, re.IGNORECASE|re.MULTILINE|re.DOTALL)
"""
# replace all non-ascii chars, numbers, common words
