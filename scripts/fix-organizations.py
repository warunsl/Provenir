from pprint import pprint
import json
import pymongo
from pymongo import MongoClient

connection = MongoClient()
db = connection.provenir
collection = db.organization

entities = []


def get_entities():
    global entities
    entities_cursor = collection.find()
    for entity in entities_cursor:
        entities.append(entity['entity_url'])
    print len(entities)


def fix_entities():
    with open('', 'rb') as jsonfile:
        for line in jsonfile:
            try:
                records = json.loads(line)
                for record in records:
            except TypeError, e:
                print "JSON format error!"
                print e


def main():
    get_entities()
    # fix_entities()


if __name__ == '__main__':
    main()