from flask import Flask
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from datetime import datetime
import requests
import json
import os

DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_PORT = os.environ.get('DATABASE_PORT')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSW = os.environ.get('DATABASE_PASSW')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
BROKER_HOST = os.environ.get('BROKER_HOST')
BROKER_PORT = os.environ.get('BROKER_PORT')
API_KEY = os.environ.get('API_KEY')


LOC_API = 'https://m.avito.ru/api/1/slocations'
QUERY_API = 'https://m.avito.ru/api/9/items'
DATABASE_URI = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(DATABASE_USER, DATABASE_PASSW, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME)
BROKER_URL = 'amqp://{}:{}'.format(BROKER_HOST, BROKER_PORT)

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = BROKER_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

db = SQLAlchemy(app)

celery = Celery('app', broker=app.config['CELERY_BROKER_URL'])



class Count(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(64), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    pair_id = db.Column(db.Integer, db.ForeignKey('pair.id'))


class Pair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(64), nullable=False)
    q = db.Column(db.String(64), nullable=False)
    counts = db.relationship('Count', backref='p')


def get_count(query: str, region: str) -> int:

    loc_resp = requests.get(LOC_API, params={'key': API_KEY, 'q': region})
    loc_id = loc_resp.json()['result']['locations'][0]['id']
    query_resp = requests.get(QUERY_API, params={'key': API_KEY, 'locationId': loc_id, 'query': query})
    count = query_resp.json()['result']['totalCount']

    return count


@celery.task
def update_pairs():
    print(Pair.query.all())
    for pair in Pair.query.all():
        query = pair.q
        region = pair.region
        time = datetime.now()
        count = get_count(query, region)
        new_count = Count(date=time.strftime('%H:%M %d/%m/%y'), count=count, p=pair)
        db.session.add(new_count)
        db.session.commit()
        

def add_new_pair(region: str, query: str) -> int:
    new_query_pair = Pair(q=query, region=region)
    db.session.add(new_query_pair)
    db.session.commit()
    return new_query_pair.id


@app.route('/add', methods=['POST'])
def add():

    new_pair = request.json
    query = new_pair['query']
    region = new_pair['region']
    id = add_new_pair(region, query)

    return jsonify({'id': id})


def get_counts_by_id(id: int):
    counts = []
    for count in Count.query.filter_by(pair_id=id).all():
        counts.append({
            'time': count.date,
            'count': count.count
        })
    return counts


@app.route('/stat')
def stat():
    id = int(request.args.get('id'))
    counts = get_counts_by_id(id)
    return jsonify(counts)


celery.conf.beat_schedule = {

    'calling-api-every-30-seconds': {
        'task': 'app.update_pairs',
        'schedule': 120.0,
    }
}







