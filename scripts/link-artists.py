from pprint import pprint
import re
import csv
import json
import pymongo
from pymongo import MongoClient

common_urls = []

connection = MongoClient()
db = connection.provenir
collection = db.artist


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
    get_common_linked_urls()
    update_collection()
    fix_duplicate_dbpedia()


if __name__ == '__main__':
    main()