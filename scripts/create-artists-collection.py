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
        "birth_date":"",
        "death_date":"",
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

def add_nga_artists_to_collection():
    pass


def add_getty_artists_to_collection():
    pass


def main():
    add_nga_artists_to_collection()
    add_getty_artists_to_collection()


if __name__ == '__main__':
    main()
