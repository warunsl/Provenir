import os
import csv
import sys
import json
import pymongo
from utils import is_csv
from pymongo import MongoClient

fields = ["PI Picture No.", "Artist Name", "Title", "Institution",
          "Accession No.", "Format/Support", "Comments", "Add'l Subjects",
          "Sale Date", "Sale Notes", "Date", "Owner/Location", "Notes",
          "Copyright"]
arts = set()
connection = MongoClient()
db = connection.gladondb
collection = db.artdata


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


# def is_csv(filename):
#     global fields
#     with open(filename, 'rb') as csvfile:
#         try:
#             csv_reader = csv.reader(csvfile)
#             for row in csv_reader:
#                 first_line = row
#                 try:
#                     elements = first_line[0].strip().split(',')
#                 except Exception, IndexError:
#                     raise csv.Error
#                 for element in elements:
#                     if element not in fields:
#                         raise csv.Error
#                 break
#             csvfile.seek(0)
#         except csv.Error:
#             print "not a csv file, skipping", filename
#             return False
#     csvfile.close()
#     return True
def create_arts_file(source):
    if source == "getty":
        with open("getty-arts", "w") as outfile:
            for art in arts:
                outfile.write(convert(art))
                outfile.write("\n")
    else:
        with open("nga-arts", "w") as outfile:
            for art in arts:
                outfile.write(art)
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


def post_process_nga_arts():
    pass


def get_nga_arts():
    global arts
    arts = set()
    with open("artdata.json", "rb") as ngafile:
        for line in ngafile:
            try:
                line_object = json.loads(line)
                print line_object["title"]
                arts.append(line_object["title"])
            except Exception, TypeError:
                print "JSON format error"
                sys.exit(1)
    ngafile.close()


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
    # post_process_nga_arts()
    # create_arts_file("nga")


if __name__ == '__main__':
    main()
