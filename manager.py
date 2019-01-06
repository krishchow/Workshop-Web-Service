from database import *
from flask import Flask, jsonify, abort, request,Response
import csv
import random, string
import datetime
import ast,base64
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
sqlDB = SQLAlchemy(app)

class User(sqlDB.Model):
    key = sqlDB.Column(sqlDB.String(32), unique=True, nullable=False,primary_key=True)

    def __repr__(self):
        return '<User %r>' % self.key

class Pokemon(sqlDB.Model):
    id = sqlDB.Column(sqlDB.Integer, unique=True, nullable=False,primary_key=True,autoincrement=True)
    Name = sqlDB.Column(sqlDB.String(80), unique=False, nullable=False)
    Type1 = sqlDB.Column(sqlDB.String(80), unique=False, nullable=False)
    Type2 = sqlDB.Column(sqlDB.String(80), unique=False, nullable=True)
    Total = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
    HP = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
    Attack = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
    Defense = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
    SpAttack = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
    SpDefense = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
    Speed = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
    Gen = sqlDB.Column(sqlDB.String(80), unique=False, nullable=False)
    isLegend = sqlDB.Column(sqlDB.String(80), unique=False, nullable=False)
    CreatedBy = sqlDB.Column(sqlDB.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.Name

db = myDB(sqlDB,User,Pokemon)

def check_auth(key):
    return db.verifyKey(key)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('key')
        if not check_auth(auth):
            print('login failed')
            return abort(401)
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/poke/', methods=['POST','PUT','GET','PATCH','DELETE'])
@requires_auth
def getMon():
    if request.method == 'POST':
        o=db.getPokemon(request.get_json())
        if o is None:
            return abort(404)
        return jsonify(o)
    if request.method == 'PUT':
        vals = request.get_json()
        out = {}
        for i in vals.keys():
            out[i] = vals.get(i)
        out['CreatedBy'] = request.headers.get('key')
        out['Gen'] = 8
        out['id'] = None
        if not out.get('Type2'): out['Type2'] = None
        if not out.get('Total'): out['Total'] = None
        o=db.addPokemon(out)
        if o is None:
            return abort(404)
        return jsonify(o)
    if request.method == 'GET':
        data = db.getAllPoke(request.headers.get('key'))
        if data is None:
            return abort(404)
        if len(data)==0:
            return abort(404)
        return jsonify(data)
    if request.method == 'PATCH':
        vals = request.get_json()
        out = {}
        for i in vals.keys():
            out[i] = vals.get(i)
        out['Gen'] = 8
        try:
            id = int(out.pop('id'))
        except ValueError:
            return abort(406)
        if not out.get('Type2'): out['Type2'] = None
        if not out.get('Total'): out['Total'] = None
        o=db.updatePoke(request.headers.get('key'), id, out)
        if o is 'noaccess':
            return abort(401)
        elif o is 'notfound':
            return abort(404)
        elif o is 'inperror':
            return abort(406)
        else:
            return jsonify(o)
    if request.method == 'DELETE':
        o=db.deletePokemon(request.headers.get('key'), request.get_json())
        if o is 'noaccess':
            return abort(401)
        elif o is 'notfound':
            return abort(404)
        elif o is 'inperror':
            return abort(406)
        else:
            return jsonify(o)

if __name__ == '__main__':
    #print(db.genKeys(5))
    app.run(debug=True)
    #app.run(host= '0.0.0.0')