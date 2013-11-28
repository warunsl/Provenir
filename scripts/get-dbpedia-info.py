import os
import csv
import sys
import json
from pprint import pprint
from BeautifulSoup import BeautifulSoup
from utils import query_sparql, get_dirs, get_files

artists = {}
nga_source = {}
already_artists = []


# Converts the encoded keys in the dictionary to string
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


def get_info_from_nga(artist):
    '''

    '''
    # print "get_info_from_nga"
    artist = unicode(BeautifulSoup(artist, convertEntities=
                                   BeautifulSoup.HTML_ENTITIES))
    result = {}
    try:
        entry = nga_source[artist]
        span = entry["lifespan"]
        if span and span is not '' and '-' in span:
            result["birth_date"] = span.split("-")[0].strip()
            result["death_date"] = span.split("-")[1].strip()
        else:
            result["birth_date"] = ""
            result["death_date"] = ""
        result["short_descr"] = ""
        result["long_descr"] = entry["description"]
        result["movement"] = ""
        return result
    except KeyError, e:
        raise e
        print "Error! Artist not found or JSON file error"
        sys.exit(1)


def build_nga_source_map(artists):
    # print "build_nga_source_map"
    for artist in artists:
        # Need to transform the artist name in first name
        # last name format
        try:
            name = artist[u'name']
            name = unicode(BeautifulSoup(name, convertEntities=
                                         BeautifulSoup.HTML_ENTITIES))
            fullname = name.strip().split(',')
            if len(fullname) == 2:
                nga_source[fullname[1].strip() + ' ' +
                           fullname[0].strip()] = artist
            else:
                nga_source[name.strip()] = artist
        except Exception, e:
            raise e
            print "Exception"


def preprocess_nga():
    '''
        The nga source file has over 12000 entries.
        Preprocessing it to create a map with artist
        name as the key. This will give us a near
        constant retrieval
    '''
    # print "preprocess_nga"
    nga_artist_source = get_files()["nga-artists"]
    with open(nga_artist_source, 'rb') as jsonfile:
        for line in jsonfile:
            try:
                entry = json.loads(line)
                entry = convert(entry)
                artists_entry = entry["artists"]
                build_nga_source_map(artists_entry)
            except Exception, e:
                pass
    jsonfile.close()


def get_info_from_dbpedia(artist_url):
    result = {}
    result["birth_date"] = query_sparql(artist_url, "birth date")
    result["death_date"] = query_sparql(artist_url, "death date")
    result["short_descr"] = query_sparql(artist_url, "short description")
    result["long_descr"] = query_sparql(artist_url, "long description")
    result["movement"] = query_sparql(artist_url, "movement")
    return result


def get_resource_url(row):
    urls = row[1:]
    for item in urls:
        if "dbpedia" in item:
            return item
        else:
            return row[3]


def process_nga_artists():
    # print "process_nga_artists"
    nga_reconciled_artists = get_files()["nga-artists-dbpedia"]

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

    with open('nga-artists-dbpedia-info.csv', 'a') as opfile:
        csvwriter = csv.writer(opfile, delimiter=',', quotechar='"',
                               quoting=csv.QUOTE_ALL)
        csvwriter.writerow(["Name", "Url", "Source", "Birth Date",
                            "Death Date", "Short description",
                            "Long description", "Movement"])
        processed = 0
        for artist, info in artists.items():
            if artist not in already_artists:
                if "dbpedia" in info[1]:
                    result = get_info_from_dbpedia(info[1])
                    # print result
                else:
                    result = get_info_from_nga(artist)
                artist = convert(artist)
                name = artist
                url = info[1]
                source = "nga"
                birth_date = result["birth_date"]
                birth_date = convert(birth_date)
                death_date = result["death_date"]
                death_date = convert(death_date)
                short_descr = result["short_descr"]
                short_descr = convert(short_descr)
                long_descr = result["long_descr"]
                long_descr = convert(long_descr)
                movement = result["movement"]
                movement = convert(movement)
                csvwriter.writerow([name, url, source, birth_date,
                                    death_date, short_descr,
                                    long_descr, movement])
                processed += 1
                print processed
    opfile.close()


def process_getty_artists():
    getty_reconciled_artists = get_files()["getty-artists-dbpedia"]
    with open(getty_reconciled_artists, 'rb') as gettyfile:
        csv_reader = csv.reader(gettyfile)
        with open('getty-artists-dbpedia-info.csv', 'a') as opfile:
            csvwriter = csv.writer(opfile, delimiter=',', quotechar='"',
                                   quoting=csv.QUOTE_ALL)
            csvwriter.writerow(["Name", "Url", "Source", "Birth Date",
                                "Death Date", "Short description",
                                "Long description", "Movement"])
            processed = 0
            for row in csv_reader:
                url = row[2]
                name = row[0]
                source = "getty"
                if "dbpedia" in url:
                    result = get_info_from_dbpedia(url)
                    birth_date = result["birth_date"]
                    birth_date = convert(birth_date)
                    death_date = result["death_date"]
                    death_date = convert(death_date)
                    short_descr = result["short_descr"]
                    short_descr = convert(short_descr)
                    long_descr = result["long_descr"]
                    long_descr = convert(long_descr)
                    movement = result["movement"]
                    movement = convert(movement)
                else:
                    birth_date, death_date, short_descr, long_descr,
                    movement = "", "", "", "", ""
                csvwriter.writerow([name, url, source, birth_date,
                                   death_date, short_descr,
                                   long_descr, movement])
                processed += 1
                print processed
    gettyfile.close()


def read_partially_written_file():
    with open('nga-artists-dbpedia-info.csv', 'rb') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            already_artists.append(row[0])
    print "Already processed artists, ", len(already_artists)


def main():
    preprocess_nga()
    # process_nga_artists()
    process_getty_artists()


if __name__ == '__main__':
    main()
