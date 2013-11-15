import json
import os
from pprint import pprint

artists_set = set()


# Converts the unicode keys in the dictionary to string
def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for
                key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def process_artists(artists_list):
    global artists_set

    for artist in artists_list:
        name = artist[u'name']
        # print name
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
                print "Not a valid json record. Slipping ..."
    jsonfile.close()

    with open('nga-artists', 'w') as outfile:
        for artist in artists_set:
            outfile.write(artist)
            outfile.write('\n')
    outfile.close()


if __name__ == '__main__':
    main()
