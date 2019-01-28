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


def attributeProcessing(inputDict: dict, rmID: bool):
    inputDict['Gen'] = 8
    try:
        inputDict['Attack'] = int(inputDict['Attack'])
        inputDict['Defense'] = int(inputDict['Defense'])
        inputDict['HP'] = int(inputDict['HP'])
        inputDict['SpAttack'] = int(inputDict['SpAttack'])
        inputDict['SpDefense'] = int(inputDict['SpDefense'])
        inputDict['Speed'] = int(inputDict['Speed'])
    except KeyError:
        raise badRequest
    except ValueError:
        raise notAcceptable
    if not inputDict.get('Type2'):
        inputDict['Type2'] = ""
    if not inputDict.get('Total'):
        inputDict['Total'] = None
    if rmID:
        inputDict['id'] = None


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
            pokeId = int(inputDict['id'])
            dbEntry = self.Poke.query.filter_by(id=pokeId).first()
        except ValueError:
            raise notAcceptable
        except KeyError:
            raise badRequest
        if dbEntry is None:
            raise notExist
        dbDict = dbEntry.__dict__
        dbDict.pop('_sa_instance_state')
        dbDict.pop('CreatedBy')
        return dbDict

    def addPokemon(self, key: str, inputDictionary: dict) -> dict:
        # preprocessing
        attributeProcessing(inputDictionary, True)
        # preprocessing done
        inputDictionary['CreatedBy'] = key
        modelColumns = [column.key for column in self.Poke.__table__.columns]
        if sorted(modelColumns) != sorted(list(inputDictionary.keys())):
            raise badRequest
        try:
            inputDictionary['Total'] = \
                                    inputDictionary['Attack'] + \
                                    inputDictionary['Defense'] + \
                                    inputDictionary['HP'] + \
                                    inputDictionary['SpAttack'] + \
                                    inputDictionary['SpDefense'] + \
                                    inputDictionary['Speed']
        except ValueError:
            raise notAcceptable
        newPoke = self.Poke(**inputDictionary)
        self.database.session.add(newPoke)
        self.database.session.flush()
        id = newPoke.id
        self.database.session.commit()
        return {'id': id}

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
        try:
            pokeid = int(attributes.pop('id'))
        except ValueError:
            raise notAcceptable
        except KeyError:
            raise badRequest
        pokeRow = self.Poke.query.filter_by(id=pokeid)
        if pokeRow.first() is None:
            raise notExist
        if pokeRow.first().CreatedBy != userKey:
            raise noPermissions
        dbEntry = pokeRow.first().__dict__
        try:
            for i in attributes:
                dbEntry[i] = attributes[i]
            attributeProcessing(attributes, False)
            dbEntry['Total'] = \
                dbEntry['Attack'] + \
                dbEntry['Defense'] + \
                dbEntry['HP'] + \
                dbEntry['SpAttack'] + \
                dbEntry['SpDefense'] + \
                dbEntry['Speed']
            dbEntry.pop('_sa_instance_state')
            newPoke = self.Poke(**dbEntry)
            self.database.session.merge(newPoke)
            self.database.session.commit()
        except ValueError:
            raise notAcceptable
        except IntegrityError:
            raise notAcceptable
        except KeyError:
            raise badRequest
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
