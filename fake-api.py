from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/api')
def api():
    return jsonify({'count': random.randint(1, 12)})

app.run(port=5005)