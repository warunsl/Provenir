import pymongo
from pprint import pprint
from pymongo import MongoClient
from BeautifulSoup import BeautifulSoup

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
        "organizations" : [
            "",
            ""
        ]
    }
'''

connection = MongoClient()
db = connection.provenir
collection = db.art
artist_collection = db.artist
org_collection = db.organization

gldb = connection.gladondb
artdata_collection = gldb.artdata
entity_collection = gldb.entitytoart

art_entity_map = {}
entity_art_map = {}
arts = []
transformed_arts = []


def create_art_collection():
    for art in transformed_arts:
        try:
            collection.insert(art)
        except pymongo.errors.DuplicateKeyError, e:
            print e


def transform_art_and_create_collection():
    global transformed_arts
    for art in arts:
        # title = unicode(BeautifulSoup(art["title"], convertEntities=BeautifulSoup.HTML_ENTITIES))
        art_dict = {}
        art_dict["title"] = art["title"]

        image = art["imagepath"]
        if image[:4] not in "http":
            image = "http://www.nga.gov" + image
        art_dict["image"] = image

        nga_artist = art["artists - url"]
        res = artist_collection.find_one({'source':'nga', 'nga-data.url':nga_artist})
        if res:
            art_dict["artist"] = res['name']
        else:
            art_dict["artist"] = ""

        art_dict["short_description"] = art["creditline"]
        try:
            art_dict["organizations"] = art_entity_map[art["id"]]
        except KeyError:
            art_dict["organizations"] = []

        art_dict["source"] = "nga"
        art_dict["nga-data"] = art
        try:
            collection.insert(art_dict)
        except pymongo.errors.DuplicateKeyError, e:
            print e
        

def create_org_collection():
    for entity, arts in entity_art_map.items():
        org_collection.insert({'entity_url':entity, 'nga-art-ids':arts})


def get_organizations():
    entities = []
    global entity_art_map
    global art_entity_map
    unique_arts = set()
    entity_cursor = entity_collection.find({'type':'Organization'})
    for entity in entity_cursor:
        entities.append(entity)
    for entity in entities:
        entity_art_map[entity['entityURL']] = entity['arts']
    for entity, arts in entity_art_map.items():
        for art in arts:
            unique_arts.add(art)
    for art in unique_arts:
        for entity in entity_art_map.keys():
            if art in entity_art_map[entity]:
                try:
                    art_entity_map[art].append(entity)
                except KeyError:
                    art_entity_map[art] = [entity]


def get_nga_arts():
    global arts
    arts_cursor = artdata_collection.find()
    for art in arts_cursor:
        arts.append(art)


def main():
    get_nga_arts()
    get_organizations()
    transform_art_and_create_collection()


if __name__ == '__main__':
    main()
