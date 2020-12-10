from flask import Flask
from flask import request
from flask import jsonify
from celery import Celery
from datetime import datetime
import requests
import json

app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = 'amqp://localhost:5672'

celery = Celery('app', broker=app.config['CELERY_BROKER_URL'])

URL = 'http://localhost:5005/api'


def get_count(query: str, region: str) -> int:
    resp = requests.get(URL, params={'query': query, 'region': region})
    return resp.json()['count']


@celery.task
def update_pairs():

    with open('pairs.json') as f:
        data = f.read()
        pairs = json.loads(data)

    for pair in pairs:
        query = pair['query']
        region = pair['region']
        time = datetime.now()
        count = get_count(query, region)
        pair['counts'].append({'time': time.strftime('%H:%M %d/%m/%y'), 'count': count})
        print('Pair (%s, %s) have been updated :)'.format(query, region))

    with open('pairs.json', 'w') as f:
        f.write(json.dumps(pairs))


def add_new_pair(region: str, query: str) -> int:

    with open('pairs.json', 'r') as f:
        data = f.read()
        pairs = json.loads(data)

    pairs.append({
        'id': len(pairs) + 1,
        'query': query,
        'region': region,
        'counts': []
    })

    with open('pairs.json', 'w') as f:
        f.write(json.dumps(pairs))
    

    return len(pairs) + 1



@app.route('/add', methods=['POST'])
def add():

    new_pair = request.json
    query = new_pair['query']
    region = new_pair['region']

    id = add_new_pair(region, query)

    return jsonify({'id': id})



def get_counts_by_id(id: int):
    with open('pairs.json') as f:
        data = f.read()
    pairs = json.loads(data)
    return pairs[id - 1]['counts']


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









