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

    for artist in artists:
        print artist
        for term in wrong_terms:
            if term in artist.lower():
                idx.append(artist.lower().index(term))
        if len(idx) != 0:
            print artist[:min(idx)]
            new_artists.add(artist[:min(idx)])
        else:
            print artist
            new_artists.add(artist)
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

    for artist in artists:
        if '[' not in artist or ']' not in artist:
            new_artists.add(artist)

    artists = new_artists


def create_artists_file():
    global artists

    with open('artistsgetty.txt', 'w') as opfile:
        for artist in artists:
            opfile.write(artist)
            opfile.write('\n')
    opfile.close()


def is_csv(filename):
    with open(filename, 'rb') as csvfile:
        try:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                first_line = row
                try:
                    elements = first_line[0].strip().split(',')
                except Exception, IndexError:
                    raise csv.Error
                for element in elements:
                    if element not in fields:
                        raise csv.Error
                break
            csvfile.seek(0)
        except csv.Error:
            print "not a csv file, skipping", filename
            return False
    csvfile.close()
    return True


def get_artists(filename):
    global fields
    global artists
    print "processing file ", filename
    with open(filename, 'rb') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            artists.add(row[1])
    print "Total number of unique artists", len(artists)
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
