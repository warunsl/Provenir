import sys
import json
import pymongo
from utils import get_files
from pprint import pprint
from pymongo import MongoClient
from BeautifulSoup import BeautifulSoup

connection = MongoClient()
db = connection.provenir
collection = db.artist


nga_artists = []
nga_result_map = {}


# Converts the encoded keys in the dictionary to string
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


def output_to_file():
    global nga_result_map
    print len(nga_result_map.keys())
    with open("fixed-nga", "w") as outfile:
        for k, v in nga_result_map.items():
            outfile.write(convert(k))
            outfile.write(" ")
            outfile.write(v[0])
            outfile.write(" ")
            outfile.write(v[1])
            outfile.write(" ")
            outfile.write("\n")
    outfile.close()


def build_nga_source_map(artists):
    print len(artists)
    global nga_result_map
    for artist in artists:
        # Need to transform the artist name in first name
        # last name format
        try:
            name = artist[u'name']
            name = unicode(BeautifulSoup(name, convertEntities=
                                         BeautifulSoup.HTML_ENTITIES))
            print name
            nationality = artist[u'nationality']
            nationality = unicode(BeautifulSoup(nationality, convertEntities=
                                                BeautifulSoup.HTML_ENTITIES))
            imagepath = artist[u'imagepath']
            imagepath = unicode(BeautifulSoup(imagepath, convertEntities=
                                              BeautifulSoup.HTML_ENTITIES))
            fullname = name.strip().split(',')
            if len(fullname) == 2:
                nga_result_map[fullname[1].strip() + ' ' +
                               fullname[0].strip()] = [nationality, imagepath]
            else:
                nga_result_map[name.strip()] = [nationality, imagepath]
        except Exception, e:
            raise e
            print "Exception"
    print "End"
    print len(nga_result_map.keys())


def process_nga_source():
    nga_artist_source = get_files()["nga-artists"]
    with open(nga_artist_source, 'rb') as jsonfile:
        for line in jsonfile:
            try:
                entry = json.loads(line)
                entry = convert(entry)
                artists_entry = entry["artists"]
                build_nga_source_map(artists_entry)
            except Exception, e:
                pass
    jsonfile.close()


def get_nga_artists_from_mongo():
    cursor = collection.find({"source": "nga"},
                             fields={"_id": False, "name": True})
    for item in cursor:
        artist = unicode(BeautifulSoup(item["name"], convertEntities=
                                       BeautifulSoup.HTML_ENTITIES))
        nga_artists.append(artist)
    print len(nga_artists)


def main():
    get_nga_artists_from_mongo()
    process_nga_source()
    pprint(nga_result_map)
    output_to_file()


if __name__ == '__main__':
    main()
