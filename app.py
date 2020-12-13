from flask import Flask
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from datetime import datetime
import requests
import json
import os

DATABASE_URI = 'postgresql+psycopg2://postgres:postgres@db:5432/avito_test'

app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = 'amqp://broker:5672'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

db = SQLAlchemy(app)

celery = Celery('app', broker=app.config['CELERY_BROKER_URL'])

URL = 'http://0.0.0.0:5005/api'

FAKE_URL = os.environ.get('FAKE_URL')


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
    print(FAKE_URL)
    resp = requests.get('http://' + FAKE_URL + ":5005/api", params={'query': query, 'region': region})
    return resp.json()['count']


@celery.task
def update_pairs():

    for pair in Pair.query.all():
        query = pair.q
        region = pair.region
        time = datetime.now()
        count = get_count(query, region)
        new_count = Count(date=time.strftime('%H:%M %d/%m/%y'), count=count, p=pair)
        db.session.add(new_count)
        db.session.commit()
        #pair['counts'].append({'time': time.strftime('%H:%M %d/%m/%y'), 'count': count})
        print('Pair (%s, %s) have been updated :)'.format(q, region))

  #  with open('pairs.json') as f:
  #      data = f.read()
  #      pairs = json.loads(data)

  #  for pair in pairs:
  #      query = pair['query']
  #      region = pair['region']
  #      time = datetime.now()
  #      count = get_count(query, region)
  #      pair['counts'].append({'time': time.strftime('%H:%M %d/%m/%y'), 'count': count})
  #      print('Pair (%s, %s) have been updated :)'.format(query, region))

  #  with open('pairs.json', 'w') as f:
  #     f.write(json.dumps(pairs))
        


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
    #with open('pairs.json') as f:
    #    data = f.read()
    #pairs = json.loads(data)
    #return pairs[id - 1]['counts']
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
   # 'add-every-30-seconds': {
   #     'task': 'tasks.add',
   #     'schedule': 30.0,
   #     'args': (16, 16)
   # },

    'calling-api-every-30-seconds': {
        'task': 'app.update_pairs',
        'schedule': 30.0,
    }
}







