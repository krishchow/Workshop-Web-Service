from flask_sqlalchemy import SQLAlchemy
from csv import DictReader
from helperFunctions import randGen


class myDB:
    def __init__(self, db: SQLAlchemy, userdb: SQLAlchemy.Model,
                 pdb: SQLAlchemy.Model):
        self.database = db
        self.User = userdb
        self.Poke = pdb
        self.initDb()

    def initDb(self):
        self.database.session.commit()
        self.database.create_all()
        if not self.User.query.filter_by(key='admin').count():
            # First time configuration
            admin = self.User(key='admin')
            self.database.session.add(admin)
            self.database.session.commit()
            inputData = open('pokemon.csv', encoding="ISO-8859-1")
            reader = list(DictReader(inputData))
            for i in reader:
                i['id'] = None
                current = self.Poke(**i)
                self.database.session.add(current)
            self.database.session.commit()

    def getPokemon(self, idmap):
        try:
            poke = self.Poke.query.filter_by(id=int(idmap['id'])).first()
        except ValueError:
            return 'must be an integer'
        except KeyError:
            return 'must be an id key'
        if poke is None:
            return None
        dct = poke.__dict__
        dct.pop('_sa_instance_state')
        dct.pop('CreatedBy')
        return dct

    def addPokemon(self, attributeDct):
        mykeys = [column.key for column in self.Poke.__table__.columns]
        if sorted(mykeys) == sorted(list(attributeDct.keys())):
            try:
                attributeDct['Total'] = \
                                        int(attributeDct['Attack']) + \
                                        int(attributeDct['Defense']) + \
                                        int(attributeDct['HP']) + \
                                        int(attributeDct['SpAttack']) + \
                                        int(attributeDct['SpDefense'])
            except ValueError:
                return None
            newPoke = self.Poke(**attributeDct)
            self.database.session.add(newPoke)
            self.database.session.flush()
            id = newPoke.id
            self.database.session.commit()
            return {'id': id}
        else:
            return None

    def verifyKey(self, key):
        row = self.User.query.filter_by(key=key).first()
        if row is None:
            return False
        else:
            return True

    def genKeys(self, amount):
        outKeys = []
        for _ in range(amount):
            key = randGen()
            outKeys.append(key)
            current = self.User(key=key)
            self.database.session.add(current)
        try:
            self.database.session.commit()
        except Exception:
            return "Failed"
        return outKeys

    def getAllPoke(self, userKey):
        rows = self.Poke.query.filter_by(CreatedBy=userKey).all()
        out = [poke.__dict__['id'] for poke in rows]
        return out

    def updatePoke(self, userid, pokeid, attributeDct):
        pokeRow = self.Poke.query.filter_by(id=pokeid)
        if pokeRow.first() is None:
            return 'notfound'
        if pokeRow.first().CreatedBy != userid:
            return 'noaccess'
        ad = pokeRow.first().__dict__
        try:
            for i in attributeDct:
                ad[i] = attributeDct[i]
            ad['Total'] = int(ad['Attack']) + int(ad['Defense']) + \
                int(ad['HP']) + \
                int(ad['SpAttack']) + \
                int(ad['SpDefense']) + int(ad['Speed'])
            ad.pop('_sa_instance_state')
            newPoke = self.Poke(**ad)
            self.database.session.merge(newPoke)
            self.database.session.commit()
        except ValueError:
            return 'inperror'
        return {pokeid: 'Success'}

    def deletePokemon(self, userid, data):
        try:
            pokeRow = self.Poke.query.filter_by(id=data['id']).first()
        except ValueError:
            return 'inperror'
        except KeyError:
            return 'inperror'
        if pokeRow is None:
            return 'notfound'
        if pokeRow.CreatedBy != userid:
            return 'noaccess'
        self.database.session.delete(pokeRow)
        self.database.session.commit()
        return {data['id']: 'Deleted'}
