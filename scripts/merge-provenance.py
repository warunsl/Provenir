import csv
import pymongo
from pymongo import MongoClient
from pprint import pprint
from BeautifulSoup import BeautifulSoup

connection = MongoClient()
db = connection.provenir
art_collection = db.art

gldb = connection.gladondb
getty_prov_collection = gldb.provenanceGetty
nga_prov_collection = gldb.ngaprovenance

getty_provenance_map = {}
nga_provenance_map = {}
common_arts = []


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for
                key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def push_getty_provenance():
    global common_arts
    # print len(common_arts)
    getty_ids = []
    for record in common_arts:
        getty_ids.append(record['getty_data']['picture_id'])

    count = 0
    getty_records = art_collection.find({'source':'getty'})
    for record in getty_records:
        if int(record['getty_data']['picture_id']) not in getty_ids:
            getty_id = int(record['getty_data']['picture_id'])
            prov_record = getty_prov_collection.find_one({'picId':getty_id})
            # print prov_record['provenanceArr']
            count += 1
            new_prov = transform_getty_prov(prov_record['provenanceArr'])
            # print record['_id']
            # print record['getty_data']['picture_id']
            art_collection.update({'_id':record['_id']}, {"$set": {"provenance":new_prov}})
            print record['_id']
    print count


def push_nga_provenance():
    nga_records = []
    nga_records_cursor = nga_prov_collection.find()
    for record in nga_records_cursor:
        nga_records.append(record)

    count = 0
    for art in nga_records:
        # pprint(art)
        old_prov = art['provenanceArr']
        new_prov = transform_nga_prov(old_prov)
        search_id = art['artId']
        record_to_update = art_collection.find_one({'nga_data.id':search_id})
        count += 1
        art_collection.update({'_id':record_to_update['_id']}, {"$set": {"provenance":new_prov}})
    print "Count ", count


def transform_nga_prov(nga_prov):
    dates = []
    new_dates = []
    for line in nga_prov:
        try:
            dates.append(line['date'])
        except KeyError:
            dates.append('NA')
    
    start_dates = dates
    end_dates = [date for date in dates[1:]]
    end_dates.append('NA')
    new_dates = zip(start_dates, end_dates)

    new_nga_prov = []
    for i in range(len(nga_prov)):
        obj = {}
        obj['startDate'] = new_dates[i][0]
        obj['endDate'] = new_dates[i][1]
        prov = convert(nga_prov[i]['provenance'])
        # prov = unicode(BeautifulSoup(nga_prov[i]['provenance'], convertEntities=BeautifulSoup.HTML_ENTITIES))
        obj['provenance'] = prov
        obj['source'] = 'nga'
        new_nga_prov.append(obj)
    # pprint(new_nga_prov)
    return new_nga_prov


def transform_getty_prov(getty_prov):
    new_getty_prov = []
    for item in getty_prov:
        obj = {}
        obj['startDate'] = item['startDate']
        obj['endDate'] = item['endDate']
        prov = convert(item['provenance'])
        # prov = unicode(BeautifulSoup(item['provenance'], convertEntities=BeautifulSoup.HTML_ENTITIES))
        obj['provenance'] = prov
        obj['source'] = 'getty'
        new_getty_prov.append(obj)
    return new_getty_prov


def get_common_arts():
    global common_art_names
    records_cursor = art_collection.find({'linked':'True'})
    for record in records_cursor:
        common_arts.append(record)


def merge_provenance():
    for art in common_arts:
        getty_id = int(art['getty_data']['picture_id'])
        getty_record = getty_prov_collection.find_one({'picId':getty_id})
        if getty_record is not None:
            try:
                getty_prov = getty_record['provenanceArr']
            except KeyError:
                # Can assign NGA provenance and proceed to the next common record
                pass
        getty_prov = transform_getty_prov(getty_prov)

        nga_id = int(art['nga_data']['id'])
        nga_record = nga_prov_collection.find_one({'artId':nga_id})
        if nga_record is not None:
            try:
                nga_prov = nga_record['provenanceArr']
            except KeyError:
                # Assign getty prov and continue
                pass
        nga_prov = transform_nga_prov(nga_prov)

        merged = getty_prov + nga_prov
        merged = sorted(merged, key=lambda item:item['startDate'] if item['startDate'].isdigit() else item['endDate'])

        art_collection.update({'_id':art['_id']}, {"$set": {"provenance":merged}})


def main():
    get_common_arts()
    # merge_provenance()
    # push_nga_provenance()
    push_getty_provenance()


if __name__ == '__main__':
    main()
