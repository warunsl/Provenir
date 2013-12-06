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
gldb = connection.gladondb
artist_collection = db.artist
artist_to_art_collection = gldb.artisttoart
art_data_collection = gldb.artdata

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/art')
def art():
    return render_template('art.html')

@app.route('/artist/<artistid>')
def artist(artistid=None):
    try:
        artist_object = artist_collection.find_one({'_id':bson.ObjectId(oid=str(artistid))})
        if artist_object:
            if artist_object['source'] == 'nga':
                # first = artist_object['nga-data']['url'].split('.html')[0]
                # nga_id = first[first.index('.') + 1:]
                nga_artist_url = artist_object['nga-data']['url']
                artist_to_art_record = artist_to_art_collection.find_one({'artistURL':nga_artist_url})
                if artist_to_art_record:
                    art_ids = artist_to_art_record['arts']
                    arts = []
                    if len(art_ids) > 0:
                        artist_object['art_ids'] = art_ids
                        for art_id in art_ids:
                            art_data_record = art_data_collection.find_one({'id':art_id})
                            if art_data_record:
                                title = unicode(BeautifulSoup(art_data_record['title'], convertEntities=
                                   BeautifulSoup.HTML_ENTITIES))
                                arts.append({'id': art_id, 'title':title, 'image':art_data_record['imagepath']})
                        artist_object['arts'] = arts
            pprint(artist_object)
            return render_template('artist.html', artist=artist_object)
        else:
            return render_template('404.html')
    except bson.errors.InvalidId, e:
        return render_template('404.html')
    
