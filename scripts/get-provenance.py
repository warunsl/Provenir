import os
import csv
from pprint import pprint

accids = {}


def get_accids():
    '''
        1. Get the accid and artist name from artistaccid.csv
        2. For each ccid, get the corresponding records from 
           getty csvs
        3. Combine all the provenance records for a particular
           art work(accid)
        4. Push that in final art json
        5. Push the entire getty strings also into the final art
           json
    '''
    global accids
    with open('artistaccid.csv', 'rb') as cafile:
        csv_reader = csv.reader(cafile)
        cc = 0
        for row in csv_reader:
            try:
                accids[row[3]].append(row)
                print accids[row[3]]
            except KeyError:
                accids[row[3]] = [row]
    cafile.close()
    print cc


def main():
    get_accids()




if __name__ == '__main__':
    main()