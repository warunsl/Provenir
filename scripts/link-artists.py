from pprint import pprint
import re
import csv
import json
import urllib
import pymongo
from pymongo import MongoClient
from BeautifulSoup import BeautifulSoup

common_urls = []

connection = MongoClient()
db = connection.provenir
collection = db.artist


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


def fix_dbpedia_artist_image_urls():
    with open('imageurls.json', 'rb') as imageurlfile:
        all_records = []
        artist_image_map = {}
        for line in imageurlfile:
            line = line.decode('utf-8')
            all_records = json.loads((line))

        print len(all_records)
        for record in all_records:
            try:
                url = record[u'imgURL'].decode('utf-8') 
                artist_image_map[record[u'url']] = url
            except (UnicodeEncodeError, KeyError) as e:
                print "Skipped.."
                pass

        print len(artist_image_map.keys())
            
        records = [record for record in collection.find({'linked':'True'})]

        print "DBpedia records ", len(records)

        for record in records:
            try:
                collection.update({"_id":record['_id']}, {"$set": {"image_url": artist_image_map[record['url']]}})
            except (Exception, KeyError) as e:
                pass

        # Verify
        print "Fixed records ", collection.find({ 'image_url' : { "$exists" : "true" } }).count()
    imageurlfile.close()    


def fix_duplicate_dbpedia():
    dbpedia_artists = []
    dbpedia_artists_cursor = collection.find({'linked':'True'})
    for record in dbpedia_artists_cursor:
        dbpedia_artists.append(record['url'])
    print "Before deduplication", len(dbpedia_artists)
    # dbpedia_artists = list(set(dbpedia_artists))
    # print "After deduplication", len(dbpedia_artists)
    count = 0
    for artist_url in dbpedia_artists:
        cursor = collection.find({'linked':'True', 'url':artist_url})
        for record in cursor:
            if record['source'] == 'nga':
                record_to_update = record
                break
            else:
                record_to_update = record
        # Remove all the artist records for this url
        collection.remove({'linked':'True', 'url':artist_url})
        # Add the one we saved
        collection.insert(record_to_update)
    dbpedia_artists_cursor = collection.find({'linked':'True'})
    print "After deduplication", len(set(list(dbpedia_artists)))


#db.test.update({"x": "y"}, {"$set": {"a": "c"}})
def update_collection():
    dbpedia_regx = re.compile("/.*dbpedia.*/", re.IGNORECASE)
    records_to_update = collection.find({"url": dbpedia_regx})
    print records_to_update.count()

    foaf_regx = re.compile("/.*xmlns.*/", re.IGNORECASE)
    records_not_to_update = collection.find({"url": foaf_regx})
    print records_not_to_update.count()

    result = collection.update({"url": foaf_regx}, {"$set": {"linked": "False"}})
    pprint(result)

    for record in records_to_update:
        if record['url'] in common_urls:
            result = collection.update({"_id": record['_id']}, {"$set": {"linked": "True"}})
        else:
            result = collection.update({"_id": record['_id']}, {"$set": {"linked": "False"}})


def get_common_linked_urls():
    with open("fril-result-common-artist.csv", "rb") as commonsfile:
        csv_reader = csv.reader(commonsfile)
        for row in csv_reader:
            common_urls.append(row[0])


def main():
    # get_common_linked_urls()
    # update_collection()
    # fix_duplicate_dbpedia()
    fix_dbpedia_artist_image_urls()


if __name__ == '__main__':
    main()