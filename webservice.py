from flask import Flask, jsonify, Response, request
from database import myDB
from exceptions import flaskException


class webservice:
    def __init__(self, app: Flask, db: myDB):
        self.app = app
        self.db = db

    def handlePOST(self, request: request) -> Response:
        try:
            database_output = self.db.getPokemon(request.get_json())
        except flaskException as e:
            return e.getPage()
        return jsonify(database_output)

    def handleGET(self, request: request) -> Response:
        try:
            database_output = self.db.getAllPoke(request.headers.get('key'))
        except flaskException as e:
            return e.getPage()
        return jsonify(database_output)

    def handleDELETE(self, request: request) -> Response:
        key = request.headers.get('key')
        try:
            database_output = self.db.deletePokemon(key, request.get_json())
        except flaskException as e:
            return e.getPage()
        return jsonify(database_output)

    def handlePATCH(self, request: request) -> Response:
        vals = request.get_json()
        jsonDictionary = {}
        for i in vals.keys():
            jsonDictionary[i] = vals.get(i)
        key = request.headers.get('key')
        try:
            database_output = self.db.updatePoke(key, jsonDictionary)
        except flaskException as e:
            return e.getPage()
        return jsonify(database_output)

    def handlePUT(self, request: request) -> Response:
        vals = request.get_json()
        jsonDictionary = {}
        jsonDictionary['CreatedBy'] = request.headers.get('key')
        for i in vals.keys():
            jsonDictionary[i] = vals.get(i)
        try:
            database_output = self.db.addPokemon(jsonDictionary)
        except flaskException as e:
            return e.getPage()
        return jsonify(database_output)

    def handleKeyGen(self, request: request) -> Response:
        generatedKey = self.db.genKeys(1)
        return jsonify(generatedKey)
