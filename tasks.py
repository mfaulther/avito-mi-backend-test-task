from celery import Celery
import requests

URL = 'http://localhost:5000/api'

app = Celery('tasks', broker='amqp://localhost:5672')

@app.task
def add(x, y):
    return x + y

app.conf.beat_schedule = {
   # 'add-every-30-seconds': {
   #     'task': 'tasks.add',
   #     'schedule': 30.0,
   #     'args': (16, 16)
   # },

    'calling-api-every-30-seconds': {
        'task': 'tasks.api_calling',
        'schedule': 30.0,
    }
}

@app.task
def api_calling():
    resp = requests.get(URL)
    j_resp = resp.json()
    return j_resp['count']
        

