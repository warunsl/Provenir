from pprint import pprint
import json
import pymongo
from pymongo import MongoClient

connection = MongoClient()
db = connection.provenir
collection = db.organization

entities_name_map = {}


def fix_entities():
    global entities_name_map
    with open('entitiesToReconcile.json', 'rb') as jsonfile:
        for line in jsonfile:
            try:
                records = json.loads(line)
                types = set()
                for record in records:
                    entities_name_map[record['url']] = record['label']

                for url, label in entities_name_map.items():
                    record_to_update = collection.find_one({'entity_url':url})
                    collection.update({"_id":record_to_update['_id']}, {"$set": {"entity_label": label}})
                print "Length", len(entities_name_map.keys())
                res = collection.find({ 'entity_label' : { "$exists" : "true" } })
                print "Updated records ", res.count()
            except TypeError, e:
                print "JSON format error!"
                print e


def main():
    fix_entities()


if __name__ == '__main__':
    main()