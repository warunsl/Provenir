import os
import csv
from utils import is_csv
from pprint import pprint

pno_map = {}
fields = ["PI Picture No.", "Artist Name", "Title", "Institution",
          "Accession No.", "Format/Support", "Comments", "Add'l Subjects",
          "Sale Date", "Sale Notes", "Date", "Owner/Location", "Notes",
          "Copyright"]


def create_input_for_open_refine():
    global pno_map
    with open('provorinput', 'w') as opfile:
        csvwriter = csv.writer(opfile, delimiter=',', quotechar='"',
                       quoting=csv.QUOTE_ALL)
        csvwriter.writerow(["pno","col1","col2","col3"])
        for k, v in pno_map.items():
            for prov in v[2]:
                csvwriter.writerow([k, v[0], v[1], prov])
        


def construct_pno_map(fl):
    '''
        1. Extract pno, (art, provenance, entry) from all the csvs
    '''
    global pno_map
    with open(fl, 'rb') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            provenance = ""
            for item in row[7:]:
                provenance = provenance + " " + item
            try:
                provenance_array = pno_map[row[0]][2]
                provenance_array.add(provenance)
                pno_map[row[0]] = (row[1], row[2], provenance_array)
            except KeyError:
                if provenance is not "":
                    pno_map[row[0]] = (row[1], row[2], set([provenance]))
                else:
                    pno_map[row[0]] = (row[1], row[2], set([]))
    csvfile.close()


def main():
    filenames = [f for f in os.listdir('.') if os.path.isfile(f)]
    for fl in filenames:
        if is_csv(fl, fields):
            construct_pno_map(fl)

    create_input_for_open_refine()


if __name__ == '__main__':
    main()
