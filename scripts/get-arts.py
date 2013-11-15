import csv
import os

fields = ["PI Picture No.", "Artist Name", "Title", "Institution",
          "Accession No.", "Format/Support", "Comments", "Add'l Subjects",
          "Sale Date", "Sale Notes", "Date", "Owner/Location", "Notes",
          "Copyright"]
arts = set()


def create_arts_file():
    global arts

    with open('artsgetty.txt', 'w') as opfile:
        for art in arts:
            opfile.write(art)
            opfile.write('\n')
    opfile.close()


def is_csv(filename):
    global fields
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


def get_arts(filename):
    global arts
    print "processing file ", filename
    with open(filename, 'rb') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            arts.add(row[2])
    print "Total number of unique arts", len(arts)
    csvfile.close()


def main():
    global arts
    filenames = [f for f in os.listdir('.') if os.path.isfile(f)]
    for fl in filenames:
        if is_csv(fl):
            get_arts(fl)

    new_arts = set()
    for art in arts:
        if '(?)' in art:
            print art
            idx = art.index('(?)')
            art = art[:idx] + art[idx+3:]
            print art
        new_arts.add(art)
    arts = new_arts

    create_arts_file()


if __name__ == '__main__':
    main()
