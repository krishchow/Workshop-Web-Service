from flask import Flask, jsonify, abort
from database import myDB


class webservice:
    def __init__(self, app: Flask, db: myDB):
        self.app = app
        self.db = db

    def handlePOST(self, request):
        database_output = self.db.getPokemon(request.get_json())
        if database_output is None:
            return abort(404)
        return jsonify(database_output)

    def handleGET(self, request):
        database_output = self.db.getAllPoke(request.headers.get('key'))
        if database_output is None:
            return abort(404)
        if len(database_output) == 0:
            return abort(404)
        return jsonify(database_output)

    def handleDELETE(self, request):
        key = request.headers.get('key')
        database_output = self.db.deletePokemon(key, request.get_json())
        if database_output is 'noaccess':
            return abort(401)
        elif database_output is 'notfound':
            return abort(404)
        elif database_output is 'inperror':
            return abort(406)
        else:
            return jsonify(database_output)

    def handlePATCH(self, request):
        vals = request.get_json()
        out = {}
        for i in vals.keys():
            out[i] = vals.get(i)
        out['Gen'] = 8
        try:
            id = int(out.pop('id'))
        except ValueError:
            return abort(406)
        if not out.get('Type2'):
            out['Type2'] = None
        if not out.get('Total'):
            out['Total'] = None
        key = request.headers.get('key')
        database_output = self.db.updatePoke(key, id, out)
        if database_output is 'noaccess':
            return abort(401)
        elif database_output is 'notfound':
            return abort(404)
        elif database_output is 'inperror':
            return abort(406)
        else:
            return jsonify(database_output)

    def handlePUT(self, request):
        vals = request.get_json()
        out = {}
        for i in vals.keys():
            out[i] = vals.get(i)
        out['CreatedBy'] = request.headers.get('key')
        out['Gen'] = 8
        out['id'] = None
        if not out.get('Type2'):
            out['Type2'] = None
        if not out.get('Total'):
            out['Total'] = None
        database_output = self.db.addPokemon(out)
        if database_output is None:
            return abort(404)
        return jsonify(database_output)

    def handleKeyGen(self, request):
        generatedKey = self.db.genKeys(1)
        return jsonify(generatedKey)
        