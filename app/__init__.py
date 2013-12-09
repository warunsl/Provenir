import bson
import pymongo
from pprint import pprint
from flask import Flask
from flask import render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
from BeautifulSoup import BeautifulSoup
from flask import request
from flask import Response
from bson.json_util import dumps


mongo_url = None 
connection = None
db = None
artist_collection = None
art_collection = None
org_collection = None
artist_to_art_collection = None


def set_up_mongo():
    print "Setting up mongo.."
    global mongo_url 
    global connection
    global db
    global artist_collection 
    global art_collection 
    global org_collection 
    global artist_to_art_collection
    parameters = []

    with open('.config', 'rb') as configfile:
        for line in configfile:
            parameters.append(line.strip())
    configfile.close()
    user, password = parameters
    mongo_url = "mongodb://{0}:{1}@linus.mongohq.com:10024/app20178630".format(user, password)
    connection = MongoClient(mongo_url)
    print connection
    db = connection.app20178630
    artist_collection = db.artist
    art_collection = db.art
    org_collection = db.organization
    artist_to_art_collection = db.artisttoart


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/viz')
def viz():
    return render_template('visualizations.html')


@app.route('/organization/<orgid>')
def organization(orgid=None):
    try:
        org_object = org_collection.find_one({'_id':bson.ObjectId(oid=str(orgid))})
        if org_object:
            # Get the art ids
            nga_art_ids = org_object['nga-art-ids']
            int_nga_art_ids = [int(i_d) for i_d in nga_art_ids]
            int_nga_art_ids = list(set(int_nga_art_ids))
            arts_cursor =  art_collection.find({ "nga_data.id": { "$in": int_nga_art_ids } })
            # art_ids = [item['_id'] for item in arts_cursor]
            # org_object['art_ids'] = art_ids

            # Get the art objects
            arts_cursor =  art_collection.find({ "nga_data.id": { "$in": int_nga_art_ids } })
            arts = [item for item in arts_cursor]
            org_object['arts'] = arts

            # Turns out there are duplicates in our database. No time to fix the db.
            # Removing duplicates based on nga_data.id here
            d = {x['nga_data']['id']: x for x in arts}
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
        # Check if the object exists
        if art_object:
            #Check if it is a NGA art
            try:
                if art_object["linked"] == 'True':
                    artist = artist_collection.find_one({'url':art_object['artist_url']})
                    artist_id = artist['_id']
                    print artist_id
                    art_object['artist_id'] = artist_id
            except KeyError:
                if art_object["source"] == 'nga':
                    artist = artist_collection.find_one({'name':art_object['artist']})
                    artist_id = artist['_id']
                    art_object['artist_id'] = artist_id

                    if len(art_object['organizations']) > 0:
                        orglist = []
                        for org in art_object['organizations']:
                            record = org_collection.find_one({  'entity_url':org})
                            orglist.append((record['_id'], record['entity_label']))
                        art_object['organizationslist'] = orglist

                elif art_object["source"] == 'getty':
                    art_object["image"] = "http://www.nga.gov/content/dam/ngaweb/placeholder-90x90.jpg"

            return render_template('art.html', art=art_object)
        else:
            return render_template('404.html')
    except bson.errors.InvalidId, e:
        return render_template('404.html')


@app.route('/artist/<artistid>')
def artist(artistid=None):
    try:
        print "artistid ", artistid
        artist_object = artist_collection.find_one({'_id':bson.ObjectId(oid=str(artistid))})
        if artist_object:
            sd = artist_object['short_description']
            ld = artist_object['long_description']
            artist_object['description'] = sd if len(sd) > len(ld) else ld
            fixed_movement = artist_object['movement'][len('http://dbpedia.org/resource/'):].replace('_', ' ')
            artist_object['movement'] = fixed_movement
            try:
                artist_object['nga_data']
            except KeyError:
                pass
                # return render_template('404.html')
            if artist_object['source'] == 'nga':
                # first = artist_object['nga_data']['url'].split('.html')[0]
                # nga_id = first[first.index('.') + 1:]
                try:
                    artist_object['linked']
                    artist_object['image'] = artist_object['image_url']
                except KeyError:
                    artist_object['image'] = "http://www.nga.gov" + artist_object['nga_data']['imagepath']

                else:
                    artist_object['image'] = artist_object['image_url']

                nga_artist_url = artist_object['nga_data']['url']
                artist_to_art_record = artist_to_art_collection.find_one({'artistURL':nga_artist_url})
                if artist_to_art_record:
                    art_ids = artist_to_art_record['arts']
                    art_ids = set(art_ids)
                    art_ids = list(art_ids)
                    arts = []
                    if len(art_ids) > 0:
                        artist_object['art_ids'] = art_ids
                        for art_id in art_ids:

                           # Get all linked arts
                            found = False
                            linked_arts_cursor = art_collection.find({'linked':'True'})
                            for record in linked_arts_cursor:
                                if art_id == int(record['nga_data']['id']):
                                    art_data_record = record
                                    found = True
                            if not found:
                                art_data_record = art_collection.find_one({'nga_data.id':art_id})
                                
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
            print "Result not found"
            return render_template('404.html')
    except bson.errors.InvalidId, e:
        print "Invalid ID"
        return render_template('404.html')


@app.route('/search/art')
def search_art():
    query = request.args.get('query')
    result = []
    cursor = db.command("text", "art" , 
        search=query,
        limit=5)
    for record in cursor['results']:
        value = record["obj"]["title"]
        try:
            record["obj"]["nga_data"]["displaydate"]
            value += ' '+str(record["obj"]["nga_data"]["displaydate"])
        except KeyError:
            pass
        obj = {
            "value": value,
            "url": "/art/"+str(record["obj"]["_id"])
            }
        result.append(obj)
    resp = Response(response=dumps(result),
                    status=200,
                    mimetype="application/json")
    return resp


@app.route('/search/artist')
def search_artist():
    query = request.args.get('query')
    result = []
    cursor = db.command("text", "artist" , 
        search=query,
        limit=5)
    for record in cursor['results']:
        obj = {
            "value": record["obj"]["name"],
            "url": "/artist/"+str(record["obj"]["_id"])
            }
        result.append(obj)
    resp = Response(response=dumps(result),
                    status=200,
                    mimetype="application/json")
    return resp

@app.route('/search/organization')
def search_org():
    query = request.args.get('query')
    result = []
    cursor = db.command("text", "organization" , 
        search=query,
        limit=5)
    for record in cursor['results']:
        obj = {
            "value": record["obj"]["entity_label"],
            "url": "/organization/"+str(record["obj"]["_id"])
            }
        result.append(obj)
    resp = Response(response=dumps(result),
                    status=200,
                    mimetype="application/json")
    return resp
