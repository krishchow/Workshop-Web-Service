import sqlite3
import random, string

class database:
    def __init__(self):
        self.initDb()
        self.max = self.count()
        
    def count(self):
        conn = sqlite3.connect(r'data.db')
        cur = conn.cursor()
        cur.execute("SELECT max(rowid) from poke")
        n = cur.fetchone()[0]
        conn.close()
        return n

    def initDb(self):
        conn = sqlite3.connect(r'data.db')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS auth (key);')
        cur.execute('INSERT INTO auth VALUES ("{0}");'.format('123456'))
        conn.commit()
        conn.close()

    def getPokemon(self,id):
        conn = sqlite3.connect(r'data.db')
        cur = conn.cursor()
        cur.execute('SELECT * from poke WHERE Id="{0}";'.format(id))
        row = cur.fetchone()
        if row == None:
            return None
        return list(row)

    def verifyKey(self,key):
        self.cur.execute('SELECT * FROM auth WHERE key="{0}";'.format(key))
        row = self.cur.fetchone()
        if row == None:
            return False
        else:
            return True

    def genKeys(self,amount):
        out= []
        for i in range(amount):
            key = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))
            self.cur.execute('INSERT INTO auth VALUES ("{0}");'.format(key))
            out.append(key)
        return out