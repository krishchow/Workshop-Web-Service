from flask import Flask, jsonify, abort, request
import sqlite3
import csv
import random, string
import datetime
import ast,base64,dill

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

def isAdmin(row):
    if int(list(row)[2]) >= 2:
        return True

def verifyKey(key):
    conn = sqlite3.connect(r'data.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM auth WHERE key="{0}";'.format(key))
    row = cur.fetchone()
    if row == None:
        return 0
    if isAdmin(row):
        return 2
    return 1

def initDb():
    conn = sqlite3.connect(r'data.db')
    cur = conn.cursor()
    #cur.execute('DROP TABLE auth;')
    #cur.execute('DROP TABLE dillDB;')
    cur.execute('CREATE TABLE IF NOT EXISTS auth (username, key, level);')
    cur.execute('CREATE TABLE IF NOT EXISTS dillDB (OriginKey, dillValue, date, itemName,runOnCall);')
    cur.execute('INSERT INTO auth VALUES ("{0}", "{1}", "{2}");'.format('admin', '123456', 2))
    conn.commit()
    conn.close()

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

@app.route('/pythonObj', methods=['GET','POST'])
def addPython():
    #123456
    #testUpload
    if request.method == 'POST':
        sentItem = request.headers.get('pythonCode')
        itemName = request.headers.get('codeName')
        key = request.headers.get('key')
        runOnCall = request.headers.get('toRun')
        stat = verifyKey(key)
        if stat < 1:
            return abort(401)
        conn = sqlite3.connect(r'data.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM dillDB WHERE itemName="{0}";'.format(itemName))
        if cur.fetchone():
            return abort(400)
        cur.execute('INSERT INTO dillDB VALUES ("{0}","{1}","{2}","{3}","{4}");'.format(key,sentItem,datetime.datetime.now(),itemName,runOnCall))
        conn.commit()
        conn.close()
        if runOnCall == 'true':
            codeBinary = ast.literal_eval(sentItem)
            code = base64.b64decode(codeBinary)
            code = dill.loads(code)
            try:
                return jsonify({'return':code.run()})
            except:
                return "upload succesful"
        else:
            return "upload succesful"
    elif request.method == 'GET':
        itemName = request.headers.get('codeName')
        key = request.headers.get('key')
        stat = verifyKey(key)
        if stat < 1:
            return abort(401)
        conn = sqlite3.connect(r'data.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM dillDB WHERE itemName="{0}";'.format(itemName))
        row = cur.fetchone()
        if not row:
            return abort(404)
        else:
            code = list(row)[1]
            if list(row)[4]=='true':
                codeBinary = ast.literal_eval(code)
                code = base64.b64decode(codeBinary)
                code = dill.loads(code)
                try:
                    return jsonify({'return':code.run()})
                except:
                    return "upload succesful"
            else:
                return jsonify({'pythonCode':code})

if __name__ == '__main__':
    initDb()
    app.run(debug=True)
    conn = sqlite3.connect(r'data.db')
    cur = conn.cursor()