from flask import Flask, jsonify, Response, request, abort
from database import myDB
from exceptions import flaskException


class webservice:
    def __init__(self, app: Flask, db: myDB):
        self.app = app
        self.db = db

    def handleGET(self, request: request) -> Response:
        '''
        This functions handles any GET HTTP requests by checking
        the request JSON which is expected to conform to the following
        standard:

        {
            "id": +int IDNumber
        }

        Based on this JSON data, the function will return a Response
        object which has the JSON body with all of the attributes
        of the database entry with id IDNumber. This response JSON
        will confirm to the following standard:

        {
            "Attack": int,
            "Defense": int,
            "Gen": int,
            "HP": int,
            "Name": string,
            "SpAttack": int,
            "SpDefense": int,
            "Speed": int,
            "Total": int,
            "Type1": string,
            "Type2": string,
            "isLegend": bool,
            "id": int IDNumber
        }
        '''
        try:
            database_output = self.db.getPokemon(request.get_json)
        except flaskException as e:
            return abort(e.getPage())
        return jsonify(database_output)

    def handleUserGET(self, request: request) -> Response:
        '''
        This functions handles any GET HTTP requests by checking
        the request headers for the user key. Then it queries the
        database for all entries with the equivlent key and it
        returns a Flask response object with a JSON body of 
        all the 'n' entry keys. This JSON takes the form:

        [
            1,
            2,
            ...
            n
        ]
        '''
        try:
            database_output = self.db.getAllPoke(request.headers.get('key'))
        except flaskException as e:
            return abort(e.getPage())
        return jsonify(database_output)

    def handleDELETE(self, request: request) -> Response:
        '''
        This function handles all DELTE HTTP requests
        by first checking for the JSON body in the request
        and verifying that it conforms to the following standard:

        {
            "id": +int IDNumber
        }

        Once the database has verified that the ID exists, it
        deletes the entry and returns a success code.
        '''
        key = request.headers.get('key')
        try:
            self.db.deletePokemon(key, request.get_json)
        except flaskException as e:
            return abort(e.getPage())
        return jsonify(success=True)

    def handlePATCH(self, request: request) -> Response:
        '''
        This function handles all PATCH HTTP requests
        by first checking for the JSON body in the request
        and verifying that it conforms to the following standard:

        {
            "Attack": +int,
            "Defense": +int,
            "Gen": -int,
            "HP": +int,
            "Name": +string,
            "SpAttack": +int,
            "SpDefense": +int,
            "Speed": +int,
            "Total": +int,
            "Type1": +string,
            "Type2": -string,
            "isLegend": -bool,
            "id": +int IDNumber
        }

        {
            IDNumber: "Success"
        }
        '''
        key = request.headers.get('key')
        try:
            self.db.updatePoke(key, request.get_json)
        except flaskException as e:
            return abort(e.getPage())
        return jsonify(success=True)

    def handlePUT(self, request: request) -> Response:
        '''
        {
            "Attack": +int,
            "Defense": +int,
            "Gen": -int,
            "HP": +int,
            "Name": +string,
            "SpAttack": +int,
            "SpDefense": +int,
            "Speed": +int,
            "Total": +int,
            "Type1": +string,
            "Type2": -string,
            "isLegend": -bool
        }
        {
            "id": int
        }
        '''
        key = request.headers.get('key')
        try:
            self.db.addPokemon(key, request.get_json)
        except flaskException as e:
            return abort(e.getPage())
        return jsonify(success=True)

    def handleKeyGen(self, request: request) -> Response:
        '''
        [
            string
        ]
        '''
        generatedKey = self.db.genKeys(1)
        return jsonify(generatedKey)
