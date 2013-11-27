import os
import sys
import csv
import json
import pymongo

'''
    Create JSON for the artist

    artist = {
        "name" : "",
        "url" : "",
        "country" : "",
        "short_description" : "",
        "long_description" : "",
        "era" : "",
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


def get_artist_details():
    '''
        For the entries that were re-conciled successfully with dbpedia
        we fetch the artist details from dbpedia by doing a sparql query

        For the rest:
        1. If it was a nga artist, we get the details from nga json
        2. Else, blanks
    '''
    global artists
    pass


def process_files():
    '''
        Creates artist dictionary with name as the Key
        name = (name, url)
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
                    artists[row[0]] = (row[0], url)
                    # print "Specific url found: ", url
                else:
                    # print "Duplicate artist found. Skipping: ", row[0]
                    pass
            except KeyError:
                artists[row[0]] = (row[0], row[3])
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
                    artists[row[0]] = (row[0], url)
                    # print "Specific url found: ", url
                else:
                    # print "Duplicate artist found. Skipping: ", row[0]
                    pass
            except KeyError:
                artists[row[0]] = (row[0], row[2])
    gettyfile.close()

    # prepare the json to be inserted into the mongo collection
    artist_json = []
    for k, v in artists.items():
        artist_dict = {}
        artist_dict["name"] = artists[k][0]
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
    get_artist_details()


if __name__ == '__main__':
    main()
