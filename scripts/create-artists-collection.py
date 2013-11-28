import os
import sys
import csv
import json
import pymongo
from SPARQLWrapper import SPARQLWrapper, JSON

'''
    Create JSON for the artist

    artist = {
        "name" : "",
        "url" : "",
        "country" : "",
        "birth-date":"",
        "death-date":"",
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

artists = {}

scripts_dir = os.getcwd()
base_dir = os.path.dirname(scripts_dir)
data_dir = os.path.abspath(os.path.join(base_dir, 'data'))
refine_dir = os.path.abspath(os.path.join(data_dir, 'refine'))

getty_reconciled_artists = os.path.abspath(os.path.join(refine_dir,
                                           'getty-artists-dbpedia.csv'))
nga_reconciled_artists = os.path.abspath(os.path.join(refine_dir,
                                         'nga-artists-dbpedia.csv'))


def get_info_from_dbpedia(artist):
    pass


def get_info_from_ngadata(artist):
    pass


def get_artist_details():
    '''
        name = (name, url, source)

        For the entries that were re-conciled successfully with dbpedia
        we fetch the artist details from dbpedia by doing a sparql query

        For the rest:
        1. If it was a nga artist, we get the details from nga json
        2. Else, store empty values
    '''
    global artists
    if len(artists) == 0:
        print "Artist information empty"
        return False
    for artist, info in artists.items():
        if "dbpedia" in info[1]:
            get_info_from_dbpedia(artist)
        elif "nga" in info[2]:
            get_info_from_ngadata(artist)
        else:
            pass


def get_resource_url(row):
    urls = row[1:]
    for item in urls:
        if "dbpedia" in item:
            return item
        else:
            return row[3]


def process_files():
    '''
        Creates artist dictionary with name as the Key
        name = (name, url, source)
    '''

    global artists

    if not os.path.exists(getty_reconciled_artists) and not os.path.exists(nga_reconciled_artists):
        print "No input files"
        return False

    with open(nga_reconciled_artists, 'rb') as ngafile:
        csv_reader = csv.reader(ngafile)
        for row in csv_reader:
            try:
                # If we hit a duplicate artist, select the one with
                # url which is not foaf:Person
                artists[row[0]]
                url = artists[row[0]][1]
                if "Person" not in url:
                    artists[row[0]] = (row[0], url, "nga")
                else:
                    url = get_resource_url(row)
                    if "dbpedia" in url:
                        artists[row[0]] = (row[0], url, "nga")  
            except KeyError:
                # Open Refine rule bug consequence : 
                # Applicable to only nga artists
                # Process the row to see if there is a dbpedia link
                artists[row[0]] = (row[0], get_resource_url(row), "nga")
    ngafile.close()

    with open(getty_reconciled_artists, 'rb') as gettyfile:
        csv_reader = csv.reader(gettyfile)
        for row in csv_reader:
            try:
                # If we hit a duplicate artist, select the one with
                # url which is not foaf:Person
                artists[row[0]]
                url = artists[row[0]][1]
                if "Person" not in url:
                    artists[row[0]] = (row[0], url, "getty")
                else:
                    if "dbpedia" in row[2]:
                        artists[row[0]] = (row[0], row[2], "getty")
            except KeyError:
                artists[row[0]] = (row[0], row[2], "getty")
    gettyfile.close()

    # prepare the json to be inserted into the mongo collection
    artist_json = []
    for k, v in artists.items():
        artist_dict = {}
        artist_dict["name"] = artists[k][0]
        artist_dict["url"] = v[1]
        artist_dict["source"] = v[2]
        artist_dict["country"] = ""
        artist_dict["short_description"] = ""
        artist_dict["long_description"] = ""
        artist_dict["era"] = ""
        artist_dict["influencer_of"] = []
        artist_dict["influenced_by"] = []
        artist_json.append(artist_dict)

    with open('mongo_artists.json', 'w') as outfile:
        outfile.write(json.dumps(artist_json))
    outfile.close()


def main():
    if not process_files():
        sys.exit(1)
    if not get_artist_details():
        sys.exit(1)


if __name__ == '__main__':
    main()
