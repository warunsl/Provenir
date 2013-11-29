from pprint import pprint
from utils import is_csv
import csv
import os

fields = ["PI Picture No.", "Artist Name", "Title", "Institution",
          "Accession No.", "Format/Support", "Comments", "Add'l Subjects",
          "Sale Date", "Sale Notes", "Date", "Owner/Location", "Notes",
          "Copyright"]
artists = set()


def remove_wrong_terms():
    global artists
    new_artists = set()
    wrong_terms = ['attribute', 'copy', 'workshop', 'style', 'studio',
                   'after', 'follower', 'possibly', 'imitator', 'forgery',
                   'school', 'manner', 'formerly', 'ascribed', 'assistant']
    idx = []

    for artist, accid, pno in artists:
        # print artist
        for term in wrong_terms:
            if term in artist.lower():
                idx.append(artist.lower().index(term))
        if len(idx) != 0:
            # print artist[:min(idx)]
            new_artists.add((artist[:min(idx)], accid, pno))
        else:
            # print artist
            new_artists.add((artist, accid, pno))
        idx = []
    artists = new_artists


def remove_non_artists():
    global artists
    new_artists = set()

    for artist, accid, pno in artists:
        if '[' not in artist or ']' not in artist:
            new_artists.add((artist, accid, pno))

    artists = new_artists


def create_artists_file():
    '''
        The file created by this is used for
        Open Refine to clean the artists.

        Open Refine output : getty-artists.csv

        Open Refine uses te above file to reconcile
        artists with dbpedia.

        Open refine output : getty-artists-dbpedia

        get-artists-nga.py uses the artists.json to
        create a file with only the artist names

        Open refine uses this file and reconciles it
        with dbpedia to produce nga-artists-dbpedia
    '''
    global artists
    pno_map = {}
    with open('artistsgetty.csv', 'w') as opfile:
        csvwriter = csv.writer(opfile, delimiter=',', quotechar='"',
                               quoting=csv.QUOTE_ALL)
        csvwriter.writerow(["ARTIST", "ACCID", "PNO"])
        for artist, accid, pno in artists:
            try:
                count = pno_map[pno][0]
                pno_map[pno] = (count + 1, [artist, accid])
            except KeyError:
                pno_map[pno] = (1, [artist, accid])
            csvwriter.writerow([artist, accid, pno])


def get_artists(filename):
    global fields
    global artists
    print "processing file ", filename
    with open(filename, 'rb') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            artists.add((row[1], row[4], row[0]))
    # print "Total number of unique artists", len(artists)
    csvfile.close()


def main():
    filenames = [f for f in os.listdir('.') if os.path.isfile(f)]
    for fl in filenames:
        if is_csv(fl, fields):
            get_artists(fl)

    remove_non_artists()
    remove_wrong_terms()
    create_artists_file()


if __name__ == '__main__':
    main()
