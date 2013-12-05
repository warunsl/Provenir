from pprint import pprint
import re
import csv
import pymongo
from pymongo import MongoClient

common_artists = set()
url_name_map = {}

connection = MongoClient()
db = connection.provenir
collection = db.artist

def remove_duplicates_from_collection():
    pass


#db.test.update({"x": "y"}, {"$set": {"a": "c"}})
def update_collection():
    dbpedia_regx = re.compile("/.*dbpedia.*/", re.IGNORECASE)
    records_to_update = collection.find({"url": dbpedia_regx})
    print records_to_update.count()
    foaf_regx = re.compile("/.*xmlns.*/", re.IGNORECASE)
    # print collection.find().count()
    records_not_to_update = collection.find({"url": foaf_regx})
    print records_not_to_update.count()
    result = collection.update({"url": dbpedia_regx}, {"$set": {"linked": "True"}})
    pprint(result)
    result = collection.update({"url": foaf_regx}, {"$set": {"linked": "False"}})
    pprint(result)


def find_common_artists():
    with open("nga-reconciled-artist", "rb") as ngafile:
        csv_reader = csv.reader(ngafile)
        for row in csv_reader:
            try:
                url_name_map[row[1]] = row[0]
            except KeyError:
                pass
    ngafile.close()

    with open("getty-reconciled-artist", "rb") as gettyfile:
        csv_reader = csv.reader(gettyfile)
        for row in csv_reader:
            try:
                url_name_map[row[1]]
                common_artists.add(row[1])
            except KeyError:
                url_name_map[row[1]] = row[0]
    gettyfile.close()


def main():
    find_common_artists()
    remove_duplicates_from_collection()
    update_collection()


if __name__ == '__main__':
    main()