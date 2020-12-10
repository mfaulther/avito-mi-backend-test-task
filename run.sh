#!/bin/bash

source venv/bin/activate
python fake-api.py &
celery -A app.celery worker --loglevel=INFO &
celery -A app.celery beat &
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run


