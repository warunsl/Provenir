import re
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


def fix_mongo_collection():
    global nga_result_map
    count = 0
    for k, v in nga_result_map.items():
        name_regx = re.compile(r'{0}'.format(k), re.IGNORECASE)
        collection_nga_artists_cursor = collection.find({"source":"nga", "name":name_regx})
        if collection_nga_artists_cursor.count() == 1:
            for record in collection_nga_artists_cursor:
                update_id = record['_id']
                collection.update({"_id":update_id}, {"$set": {"nga-data": v}})
                count += 1
                print count
        elif collection_nga_artists_cursor.count() > 1:
            print "Uh oh"
        else:
            print "No records found for ", k
    print "End of fix_mongo_collection", count
        

def build_nga_source_map(artists):
    global nga_result_map
    count = 0
    for artist in artists:
        # Need to transform the artist name in first name
        # last name format
        try:
            name = artist['name']
            # name = unicode(BeautifulSoup(name, convertEntities=
            #                              BeautifulSoup.HTML_ENTITIES))
            fullname = name.strip().split(',')
            if len(fullname) == 2:
                nga_result_map[fullname[1].strip() + ' ' +
                               fullname[0].strip()] = artist
            else:
                nga_result_map[name.strip()] = artist
            count += 1
        except Exception, e:
            raise e
            print "Exception"
    print "End of build_nga_source_map", count


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
    print "NGA artists from mongo", len(nga_artists)


def main():
    process_nga_source()
    fix_mongo_collection()


if __name__ == '__main__':
    main()
