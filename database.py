from flask_sqlalchemy import SQLAlchemy
from csv import DictReader
from random import choice
from string import ascii_lowercase, digits, ascii_uppercase
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import Model
from typing import List, Dict
from exceptions import notExist, badRequest, noPermissions, notAcceptable


def randGen() -> str:
    charList = (choice(ascii_uppercase + ascii_lowercase + digits)
                for _ in range(16))
    return ''.join(charList)


class myDB:
    def __init__(self, db: SQLAlchemy, userdb: Model,
                 pdb: Model):
        self.database = db
        self.User = userdb
        self.Poke = pdb
        self.initDb()

    def initDb(self) -> None:
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

    def getPokemon(self, inputDict: dict) -> dict:
        try:
            poke = self.Poke.query.filter_by(id=int(inputDict['id'])).first()
        except ValueError:
            raise notAcceptable
        except KeyError:
            raise badRequest
        if poke is None:
            raise notExist
        dct = poke.__dict__
        dct.pop('_sa_instance_state')
        dct.pop('CreatedBy')
        return dct

    def addPokemon(self, inputDictionary: dict) -> dict:
        # preprocessing
        inputDictionary['Gen'] = 8
        inputDictionary['id'] = None
        if not inputDictionary.get('Type2'):
            inputDictionary['Type2'] = None
        if not inputDictionary.get('Total'):
            inputDictionary['Total'] = None
        # preprocessing done
        mykeys = [column.key for column in self.Poke.__table__.columns]
        if sorted(mykeys) == sorted(list(inputDictionary.keys())):
            try:
                inputDictionary['Total'] = \
                                        int(inputDictionary['Attack']) + \
                                        int(inputDictionary['Defense']) + \
                                        int(inputDictionary['HP']) + \
                                        int(inputDictionary['SpAttack']) + \
                                        int(inputDictionary['SpDefense'])
            except ValueError:
                raise notAcceptable
            newPoke = self.Poke(**inputDictionary)
            self.database.session.add(newPoke)
            self.database.session.flush()
            id = newPoke.id
            self.database.session.commit()
            return {'id': id}
        else:
            raise badRequest

    def verifyKey(self, key: str) -> bool:
        row = self.User.query.filter_by(key=key).first()
        if row is None:
            return False
        else:
            return True

    def genKeys(self, numberOfKeys: int) -> list:
        outKeys = []
        for _ in range(numberOfKeys):
            key = randGen()
            current = self.User(key=key)
            try:
                self.database.session.add(current)
                self.database.session.commit()
                outKeys.append(key)
            except IntegrityError:
                outKeys.append("Failed")
        return outKeys

    def getAllPoke(self, userKey: str) -> List[Dict]:
        rows = self.Poke.query.filter_by(CreatedBy=userKey).all()
        out = [poke.__dict__['id'] for poke in rows]
        if len(out) == 0:
            raise notExist
        return out

    def updatePoke(self, userKey: str, attributes: dict) -> dict:
        # preprocessing
        attributes['Gen'] = 8
        try:
            pokeid = int(attributes.pop('id'))
        except ValueError:
            raise notAcceptable
        except KeyError:
            raise badRequest
        if not attributes.get('Type2'):
            attributes['Type2'] = None
        if not attributes.get('Total'):
            attributes['Total'] = None
        # preprocessing done
        pokeRow = self.Poke.query.filter_by(id=pokeid)
        if pokeRow.first() is None:
            raise notExist
        if pokeRow.first().CreatedBy != userKey:
            raise noPermissions
        ad = pokeRow.first().__dict__
        try:
            for i in attributes:
                ad[i] = attributes[i]
            ad['Total'] = int(ad['Attack']) + int(ad['Defense']) + \
                int(ad['HP']) + \
                int(ad['SpAttack']) + \
                int(ad['SpDefense']) + int(ad['Speed'])
            ad.pop('_sa_instance_state')
            newPoke = self.Poke(**ad)
            self.database.session.merge(newPoke)
            self.database.session.commit()
        except ValueError:
            raise notAcceptable
        return {pokeid: 'Success'}

    def deletePokemon(self, userKey: str, inputDict: dict) -> dict:
        try:
            pokeRow = self.Poke.query.filter_by(id=inputDict['id']).first()
        except ValueError:
            raise notAcceptable
        except KeyError:
            raise badRequest
        if pokeRow is None:
            raise notExist
        if pokeRow.CreatedBy != userKey:
            raise noPermissions
        self.database.session.delete(pokeRow)
        self.database.session.commit()
        return {inputDict['id']: 'Deleted'}
