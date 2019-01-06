import sqlite3
import random, string
from flask import jsonify
from flask_sqlalchemy import inspect

class myDB:
    def __init__(self, db, userdb, pdb):
        self.database = db
        self.User = userdb
        self.Poke = pdb
        self.initDb()

    def initDb(self):
        self.database.create_all()
        #admin = self.User(key='admin')
        #self.database.session.add(admin)
        #self.database.session.commit()

    def getPokemon(self,idmap):
        try:
            poke = self.Poke.query.filter_by(id=int(idmap['id'])).first()
        except ValueError:
            return 'must be an integer'
        except KeyError:
            return 'must be an id key'
        if poke == None:
            return None
        dct = poke.__dict__
        dct.pop('_sa_instance_state')
        dct.pop('CreatedBy')
        return dct

    def addPokemon(self,attributeDct):
        mykeys = [column.key for column in self.Poke.__table__.columns]
        if sorted(mykeys) == sorted(list(attributeDct.keys())):
            try:
                attributeDct['Total'] = int(attributeDct['Attack']) +int(attributeDct['Defense']) +int(attributeDct['HP']) +int(attributeDct['SpAttack']) +int(attributeDct['SpDefense'])
            except ValueError:
                return None
            newPoke = self.Poke(**attributeDct)
            self.database.session.add(newPoke)
            self.database.session.flush()
            id = newPoke.id
            self.database.session.commit()
            return {'id':id}
        else:
            return None

    def verifyKey(self,key):
        row = self.User.query.filter_by(key=key).first()
        if row == None:
            return False
        else:
            return True

    def genKeys(self,amount):
        outKeys = []
        for i in range(amount):
            key = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))
            outKeys.append(key)
            current = self.User(key=key)
            self.database.session.add(current)
        self.database.session.commit()
        return outKeys

    def getAllPoke(self,userKey):
        rows = self.Poke.query.filter_by(CreatedBy=userKey).all()
        out = [poke.__dict__ for poke in rows]
        for i in out:
            i.pop('_sa_instance_state')
        return out