from database import *
from flask import Flask, jsonify, abort, request,Response
import csv
import random, string
import datetime
import ast,base64
from functools import wraps

app = Flask(__name__)
db = database()

def check_auth(key):
    return db.verifyKey(key)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('key')
        if not auth or not check_auth(auth):
            return abort(401)
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return "Hello, World!"

@requires_auth
@app.route('/poke/<id>')
def getMon(id):
    o=db.getPokemon(id)
    if o is None:
        return abort(404)
    return jsonify(o)

if __name__ == '__main__':
    app.run(debug=True)