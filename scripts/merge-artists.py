import os
import json


def main():
    artists = set()
    with open('nga-artists', 'rb') as ngafile:
        for line in ngafile:
            artists.add(line)
    ngafile.close()

    with open('getty-artists', 'rb') as gettyfile:
        for line in gettyfile:
            artists.add(line)
    gettyfile.close()

    '''
        Create JSON for the artist

        artist = {
            "name" : "",
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
    artist_json = []
    for artist in artists:
        artist_dict = {}
        artist_dict["name"] = artist.strip()
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


if __name__ == '__main__':
    main()
