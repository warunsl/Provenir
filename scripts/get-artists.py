from pprint import pprint
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

    # new_artists = set()
    # for artist in artists:
    #     if 'copy' in artist.lower():
    #         idx = artist.lower().index('copy')
    #         new_artists.add(artist[:idx])
    #     else:
    #         new_artists.add(artist)
    # artists = new_artists


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
        Google Refine.
    '''
    global artists
    pno_map = {}
    with open('artistsgetty.csv', 'w') as opfile:
        csvwriter = csv.writer(opfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for artist, accid, pno in artists:
            try:
                count = pno_map[pno][0]
                pno_map[pno] = (count + 1, [artist, accid])
            except KeyError:
                pno_map[pno] = (1, [artist, accid])
            csvwriter.writerow([artist, accid, pno])
            # opfile.write(';')
            # opfile.write(accid)
            # opfile.write('\n')
    opfile.close()
    print "Printing pno map"
    for k,v in pno_map.items():
        if v[0] > 1:
            print k, pno_map[k]


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
        if is_csv(fl):
            get_artists(fl)

    remove_non_artists()
    remove_wrong_terms()
    create_artists_file()


if __name__ == '__main__':
    main()
