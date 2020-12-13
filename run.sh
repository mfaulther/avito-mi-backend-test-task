#!/bin/bash

python create.py
gunicorn -b 0.0.0.0:8080 app:app



