from database import myDB
from flask import Flask, request, Response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from webservice import webservice
from helperFunctions import _requires_auth, keyFunction, \
    generatePokeModel, generateUserModel
from functools import partial
import traceback

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

sqlDB = SQLAlchemy(app)

db = myDB(sqlDB, generateUserModel(sqlDB), generatePokeModel(sqlDB))
cntrlr = webservice(app, db)

requires_auth = partial(_requires_auth, database=db)

limiter = Limiter(
    app,
    key_func=keyFunction,
    default_limits=["30 per minute", "1 per second"],
)

@app.route('/')
def index() -> Response:
    return "Your connection is working!"


@app.route('/genKey', methods=['GET'])
@limiter.limit("1/minute", get_remote_address)
def getID() -> Response:
    try:
        return cntrlr.handleKeyGen(request)
    except Exception as e:
        traceback.print_exc()
        return abort(500)

@requires_auth
@app.route('/poke', methods=['PUT', 'GET', 'PATCH', 'DELETE'])
def getPokemon() -> Response:
    try:
        if request.method == 'PUT':
            return cntrlr.handlePUT(request)
        elif request.method == 'GET':
            return cntrlr.handleGET(request)
        elif request.method == 'PATCH':
            return cntrlr.handlePATCH(request)
        elif request.method == 'DELETE':
            return cntrlr.handleDELETE(request)
    except Exception as e:
        traceback.print_exc()
        return abort(500)

@requires_auth
@app.route('/user', methods=['GET'])
def getAllPokemon() -> Response:
    try:
        if request.method == 'GET':
            return cntrlr.handleUserGET(request)
    except Exception as e:
        traceback.print_exc()
        return abort(500)

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host= '0.0.0.0')
