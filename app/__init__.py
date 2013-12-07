import bson
import pymongo
from pprint import pprint
from flask import Flask
from flask import render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
from BeautifulSoup import BeautifulSoup

connection = MongoClient()
db = connection.provenir
artist_collection = db.artist
art_collection = db.art
org_collection = db.organization

gldb = connection.gladondb
artist_to_art_collection = gldb.artisttoart
art_data_collection = gldb.artdata

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/organization/<orgid>')
def organization(orgid=None):
    try:
        org_object = org_collection.find_one({'_id':bson.ObjectId(oid=str(orgid))})
        if org_object:
            # Get the art ids
            nga_art_ids = org_object['nga-art-ids']
            int_nga_art_ids = [int(i_d) for i_d in nga_art_ids]
            int_nga_art_ids = list(set(int_nga_art_ids))
            arts_cursor =  art_collection.find({ "nga-data.id": { "$in": int_nga_art_ids } })
            # art_ids = [item['_id'] for item in arts_cursor]
            # org_object['art_ids'] = art_ids

            # Get the art objects
            arts_cursor =  art_collection.find({ "nga-data.id": { "$in": int_nga_art_ids } })
            arts = [item for item in arts_cursor]
            org_object['arts'] = arts

            # Turns out there are duplicates in our database. No time to fix the db.
            # Removing duplicates based on nga-data.id here
            d = {x['nga-data']['id']: x for x in arts}
            org_object['arts'] = list(d.values())

            return render_template('organization.html', org=org_object)
        else:
            return render_template('404.html')
    except bson.errors.InvalidId, e:
        return render_template('404.html')


@app.route('/art/<artid>')
def art(artid=None):
    try:
        art_object = art_collection.find_one({'_id':bson.ObjectId(oid=str(artid))})
        if art_object:
            artist = artist_collection.find_one({'name':art_object['artist']})

            artist_id = artist['_id']
            art_object['artist_id'] = artist_id

            if len(art_object['organizations']) > 0:
                orglist = []
                for org in art_object['organizations']:
                    record = org_collection.find_one({'entity_url':org})
                    orglist.append((record['_id'], record['entity_label']))
                art_object['organizationslist'] = orglist
            return render_template('art.html', art=art_object)
        else:
            return render_template('404.html')
    except bson.errors.InvalidId, e:
        return render_template('404.html')


@app.route('/artist/<artistid>')
def artist(artistid=None):
    try:
        artist_object = artist_collection.find_one({'_id':bson.ObjectId(oid=str(artistid))})
        if artist_object:
            sd = artist_object['short_description']
            ld = artist_object['long_description']
            artist_object['description'] = sd if len(sd) > len(ld) else ld
            fixed_movement = artist_object['movement'][len('http://dbpedia.org/resource/'):].replace('_', ' ')
            artist_object['movement'] = fixed_movement
            try:
                artist_object['nga-data']
            except KeyError:
                return render_template('404.html')
            if artist_object['source'] == 'nga':
                # first = artist_object['nga-data']['url'].split('.html')[0]
                # nga_id = first[first.index('.') + 1:]
                if artist_object['linked'] == 'False':
                    artist_object['image'] = "http://www.nga.gov" + artist_object['nga-data']['imagepath']
                else:
                    artist_object['image'] = artist_object['image_url']

                nga_artist_url = artist_object['nga-data']['url']
                artist_to_art_record = artist_to_art_collection.find_one({'artistURL':nga_artist_url})
                if artist_to_art_record:
                    art_ids = artist_to_art_record['arts']
                    art_ids = set(art_ids)
                    art_ids = list(art_ids)
                    arts = []
                    if len(art_ids) > 0:
                        artist_object['art_ids'] = art_ids
                        for art_id in art_ids:
                            art_data_record = art_collection.find_one({'nga-data.id':art_id})
                            if art_data_record:
                                title = unicode(BeautifulSoup(art_data_record['title'], convertEntities=
                                   BeautifulSoup.HTML_ENTITIES))
                                # print art_data_record['imagepath'][:4]
                                # if art_data_record['imagepath'][:4] not in "http":
                                #     art_data_record['imagepath'] = "http://www.nga.gov" + art_data_record['imagepath']
                                arts.append({'id': art_data_record['_id'], 'title':title, 'image':art_data_record['image']})
                            else:
                                print "No records found"
                        artist_object['arts'] = arts
            return render_template('artist.html', artist=artist_object)
        else:
            return render_template('404.html')
    except bson.errors.InvalidId, e:
        return render_template('404.html')
    
