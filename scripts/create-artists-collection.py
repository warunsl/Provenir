import os
import sys
import csv
import json
import pymongo
from utils import get_files
from pymongo import MongoClient

connection = MongoClient()
db = connection.provenir
collection = db.artist
tuples_inserted = 0

'''
    Create JSON for the artist

    artist = {
        "name" : "",
        "url" : "",
        "country" : "",
        "birth_date":"",
        "death_date":"",
        "short_description" : "",
        "long_description" : "",
        "movement" : "",
        "influencer_of" : [
            1,
            2,
            3
        ],
        "influenced_by" : [
            1,
            2,
            3
        ],
        "source":""
    }
'''


def build_json_object(row):
    json_object = {}
    json_object["name"] = row[0]
    json_object["url"] = row[1]
    json_object["source"] = row[2]

    # TO-DO : We missed getting the nationality from the nga source file
    # Going back to processing it is time consuming. Will have to come
    # back later if time permits.

    # json_object["country"]
    json_object["birth_date"] = row[3]
    json_object["death_date"] = row[4]
    json_object["short_description"] = row[5]
    json_object["long_description"] = row[6]
    json_object["movement"] = row[7]
    json_object["influencer_of"] = []
    json_object["influenced_by"] = []
    return json_object


def add_nga_artists_to_collection():
    global tuples_inserted
    nga_info_file = get_files()["nga-artists-dbpedia-info"]
    with open(nga_info_file, 'rb') as ngafile:
        csv_reader = csv.reader(ngafile)
        for row in csv_reader:
            try:
                json_object = build_json_object(row)
                inserted_id = collection.insert(json_object)
                tuples_inserted += 1
                print tuples_inserted
            except TypeError:
                print "JSON type error"
                sys.exit(1)
    ngafile.close()


def add_getty_artists_to_collection():
    global tuples_inserted
    getty_info_file = get_files()["getty-artists-dbpedia-info"]
    with open(getty_info_file, 'rb') as gettyfile:
        csv_reader = csv.reader(gettyfile)
        for row in csv_reader:
            try:
                json_object = build_json_object(row)
                inserted_id = collection.insert(json_object)
                tuples_inserted += 1
                print tuples_inserted
            except TypeError:
                print "JSON type error"
                sys.exit(1)
    gettyfile.close()


def main():
    add_nga_artists_to_collection()
    add_getty_artists_to_collection()


if __name__ == '__main__':
    main()
