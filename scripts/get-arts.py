import os
import ast
import csv
import sys
import json
import pymongo
import collections
from utils import is_csv
from pymongo import MongoClient
from BeautifulSoup import BeautifulSoup

fields = ["PI Picture No.", "Artist Name", "Title", "Institution",
          "Accession No.", "Format/Support", "Comments", "Add'l Subjects",
          "Sale Date", "Sale Notes", "Date", "Owner/Location", "Notes",
          "Copyright"]
arts = set()
connection = MongoClient()
db = connection.gladondb
collection = db.artdata


# Converts the encoded keys in the dictionary to string
def convert(input, encoding):
    if isinstance(input, dict):
        return {convert(key): convert(value) for
                key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode(encoding)
    else:
        return input


def create_mongo_arts_json():
    '''
        Create JSON for the art

        art = {
            "name" : "",
            "image_url" : "",
            "artist" : "",
            "short_description" : "",
            "long_description" : "",
            "current_owner" : "",
            "era" : "",
            "provenance" : [
                1,
                2,
                3
            ],
            "museums" : [
                "",
                ""
            ]
        }
    '''
    global arts

    arts_json = []
    for art in arts:
        art_dict = {}
        try:
            art_dict["name"] = unicode(art.strip())
            art_dict["image_url"] = ""
            art_dict["artist"] = ""
            art_dict["short_description"] = ""
            art_dict["long_description"] = ""
            art_dict["current_owner"] = ""
            art_dict["era"] = ""
            art_dict["provenance"] = []
            art_dict["museums"] = []
            arts_json.append(art_dict)
        except Exception, e:
            print "Encountered unicode error on ", art

    with open('mongo_arts.json', 'w') as outfile:
        outfile.write(json.dumps(unicode(arts_json)))
    outfile.close()


def create_arts_file(source):
    if source == "getty":
        with open("getty-arts", "w") as outfile:
            for art in arts:
                outfile.write(convert(art, 'latin-1'))
                outfile.write("\n")
    else:
        with open("nga-arts", "w") as outfile:
            for art in arts:
                outfile.write(convert(art, 'latin-1'))
                outfile.write("\n")
    outfile.close()


def post_process_getty_arts():
    global arts
    new_arts = set()
    for art in arts:
        if '(?)' in art:
            idx = art.index('(?)')
            art = art[:idx] + art[idx+3:]
        new_arts.add(art)
    arts = new_arts


def get_nga_arts():
    global arts
    arts = set()
    cursor = collection.find({}, fields={"_id": False, "title": True})
    for item in cursor:
        item = ast.literal_eval(json.dumps(item))
        try:
            art = item['title'].decode('latin-1')
            arts.add(art)
        except Exception, AttributeError:
            print "Skipped ", item['title']


def get_getty_arts(filename):
    global arts
    print "processing file ", filename
    with open(filename, 'rb') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            arts.add(row[2].decode('latin-1'))
    csvfile.close()


def main():
    global arts
    filenames = [f for f in os.listdir('.') if os.path.isfile(f)]
    for fl in filenames:
        if is_csv(fl, fields):
            get_getty_arts(fl)
    post_process_getty_arts()
    create_arts_file("getty")

    # Fetching nga data is from a mongo collection
    get_nga_arts()
    create_arts_file("nga")


if __name__ == '__main__':
    main()
