import pymongo
import argparse
from pprint import pprint
from pymongo import MongoClient
from merge_provenance import transform_nga_prov
from merge_provenance import transform_getty_prov

connection = MongoClient()
db = connection.provenir
art_collection = db.art


def main():
    # Can do a command line input. No time
    getty_pic_id = 3373
    nga_art_id = 43201

    nga_record = art_collection.find_one({'nga_data.id':nga_art_id})
    nga_prov = nga_record['provenance']
    getty_record = art_collection.find_one({'getty_data.picture_id':getty_pic_id})
    getty_prov = getty_record['provenance']

    nga_prov = transform_nga_prov(nga_prov)
    getty_prov = transform_getty_prov(getty_prov)

    merged = getty_prov + nga_prov
    merged = sorted(merged, key=lambda item:item['startDate'] if item['startDate'].isdigit() else item['endDate'])

    # pprint(merged)

    print "Removing: "
    pprint(art_collection.find_one({'nga_data.id':nga_art_id}))
    art_collection.remove({'_id':nga_record['_id']})

    print "Removing: "
    pprint(art_collection.find_one({'getty_data.picture_id':getty_pic_id}))
    art_collection.remove({'_id':getty_record['_id']})

    new_record = {}
    new_record['artist'] = nga_record['artist']
    new_record['artist_url'] = nga_record['nga_data']['artists - url']

    # "artist" : "Giannicola di Paolo",
    # "artist_url" : "http://dbpedia.org/resource/Giannicolo_da_Perugia",
    # "getty_data" : {
    #     "accession_id" : "1939.1.155",
    #     "picture_id" : "2074"
    # },
    # "image" : "http://media.nga.gov/public/supplemental/objects/2/9/6/296-crop-0-90x90.jpg",
    # "linked" : "True",
    # "nga_data" : {
    #     "art_url" : "/content/ngaweb/Collection/art-object-page.296.html",
    #     "id" : "296",
    #     "artist_url" : "/content/ngaweb/Collection/artist-info.1340.html"
    # },

    new_record['linked'] = 'True'
    new_record['nga_data'] = nga_record['nga_data']
    new_record['getty_data'] = getty_record['getty_data']
    new_record['provenance'] = merged
    print "Adding: "
    pprint(new_record)
    art_collection.insert(new_record)


if __name__ == '__main__':
    main()
