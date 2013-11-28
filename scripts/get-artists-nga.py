import json
import os
from pprint import pprint
from BeautifulSoup import BeautifulSoup

artists_set = set()


# Converts the encoded keys in the dictionary to string
def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for
                key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('latin-1')
    else:
        return input


def process_artists(artists_list):
    global artists_set

    for artist in artists_list:
        name = artist[u'name']
        name = unicode(BeautifulSoup(name, convertEntities=BeautifulSoup.HTML_ENTITIES))
        fullname = name.strip().split(',')
        if len(fullname) == 2:
            artists_set.add(fullname[1].strip() + ' ' + fullname[0].strip())
        else:
            artists_set.add(name.strip())


def main():
    artists_list = []
    with open('artists.json', 'rb') as jsonfile:
        for line in jsonfile:
            try:
                entry = json.loads(line)
                entry = convert(entry)
                artists_list = entry["artists"]
                process_artists(artists_list)
            except Exception, TypeError:
                print "Not a valid json record. Skipping ..."
    jsonfile.close()

    with open('nga-artists', 'w') as outfile:
        for artist in artists_set:
            artist = convert(artist)
            outfile.write(artist)
            outfile.write('\n')
    outfile.close()


if __name__ == '__main__':
    main()
