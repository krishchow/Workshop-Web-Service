from flask import Flask, jsonify, abort, request,Response
import csv
import random, string
import datetime
import ast,base64
from functools import wraps

class WebService:
    def check_auth(username, password):
        return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/admin/add', methods=['GET'])
def addNewAuth():
    initDb()
    username = request.headers.get('user')
    level = request.headers.get('level')
    stat = verifyKey(request.headers.get('key'))
    if stat < 2:
        return abort(401)
    conn = sqlite3.connect(r'data.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM auth WHERE username="{0}";'.format(username))
    if cur.fetchone():
        return abort(409)

    key = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))
    cur.execute('INSERT INTO auth VALUES ("{0}", "{1}", "{2}");'.format(username, key, level))
    conn.commit()
    conn.close()
    return jsonify({'username':username, 'key':key, 'level':level})

@app.route('/poke/<id>')
def getMon(id):
    auth = request.headers.get('key')
    if not verifyKey(auth):
        return abort(401)

    conn = sqlite3.connect(r'data.db')
    cur = conn.cursor()
    cur.execute('SELECT * from poke WHERE Id="{0}";'.format(id))
    row = cur.fetchone()
    if row == None:
        return abort(404)
    return jsonify(list(row))