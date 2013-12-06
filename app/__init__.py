import bson
import pymongo
from flask import Flask
from flask import render_template
from pymongo import MongoClient
from bson.objectid import ObjectId

connection = MongoClient()
db = connection.provenir
artist_collection = db.artist
art_collection = db.art

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
            return render_template('artist.html', artist=artist_object)
        else:
            return render_template('404.html')
    except bson.errors.InvalidId, e:
        return render_template('404.html')
    
