import csv
import pymongo
from pprint import pprint
from pymongo import MongoClient

connection = MongoClient()
db = connection.provenir
art_collection = db.art

gldb = connection.gladondb
prov_collection = gldb.provenanceGetty

linked_picture_ids = []


def insert_getty_arts():
    global linked_picture_ids
    getty_records_cursor = prov_collection.find()
    for record in getty_records_cursor:
        if str(record["picId"]) not in linked_picture_ids:
            print "Here"
            art_object = {}
            art_object["title"] = record["title"]
            art_object["source"] = "getty"

            art_object["getty_data"] = {}
            art_object["getty_data"]["picture_id"] = record["picId"]
            art_object["getty_data"]["accession_id"] = record["accession"]

            art_object["provenance"] = record["provenanceArr"]

            art_collection.insert(art_object)
        else:
            print "Not there"
            provenance = []
            res = art_collection.find_one({'getty_data.picture_id':str(record["picId"])})
            art_collection.update({"_id":res["_id"]}, {"$set" : {"provenance": provenance}})


def insert_linked_arts():
    global linked_picture_ids
    with open('linked-arts.csv', 'rb') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            art_object = {}
            art_object["title"] = row[0] if len(row[0]) > len(row[1]) else row[1]
            art_object["artist"] = row[9]
            art_object["artist_url"] = row[6]
            art_object["linked"] = "True"
            res = art_collection.find_one({'nga_data.id':int(row[3])})
            art_object["image"] = res["image"]

            art_object["nga_data"] = {}
            art_object["nga_data"]["id"] = row[3]
            art_object["nga_data"]["art_url"] = row[5]
            art_object["nga_data"]["artist_url"] = row[7]

            art_object["getty_data"] = {}
            art_object["getty_data"]["picture_id"] = row[2]
            art_object["getty_data"]["accession_id"] = row[4]

            art_collection.insert(art_object)

            linked_picture_ids.append(row[2])
    csvfile.close()


def main():
    art_collection.remove({'linked':'True'})
    insert_linked_arts()
    art_collection.remove({'source':'getty'})
    insert_getty_arts()


if __name__ == '__main__':
    main()
